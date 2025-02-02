import argparse

import torch
import mmcv
from mmcv.runner import load_checkpoint, parallel_test, obj_from_dict
from mmcv.parallel import scatter, collate, MMDataParallel

from mmdet import datasets
from mmdet.core import results2json_videoseg, ytvos_eval
from mmdet.datasets import build_dataloader
from mmdet.models import build_detector, detectors

import time


def single_test(model, data_loader, show=False, save_path='', max_frame_count=-1):
    """
    Arguments:
        max_frame_count (int): max number of frames used in test. <=0 means test all frames.  
    """
    model.eval()
    results = []
    dataset = data_loader.dataset
    prog_bar = mmcv.ProgressBar(len(dataset))

    infer_time_acc = 0.0
    frame_count = 0

    for i, data in enumerate(data_loader):
        # Added
        print('\ndata index i=', i)
        print('type(data)=', type(data))
        print('shape of images', data['img'][0].size())
        infer_start_time = time.time()

        with torch.no_grad():
            result = model(return_loss=False, rescale=not show, **data)

        results.append(result)

        # Added
        infer_time_acc += time.time() - infer_start_time
        frame_count += data['img'][0].size(0) 
        if max_frame_count > 0 and frame_count >= max_frame_count:
            break

        if show:
            model.module.show_result(data, result, dataset.img_norm_cfg,
                                     dataset=dataset.CLASSES,
                                     save_vis = True,
                                     save_path = save_path,
                                     is_video = True)

        batch_size = data['img'][0].size(0)
        for _ in range(batch_size):
            prog_bar.update()

    # Added
    print(f'Total infer_time: {infer_time_acc}, frame_count: {frame_count}, FPS: {frame_count/infer_time_acc}')
        
    return results


def _data_func(data, device_id):
    data = scatter(collate([data], samples_per_gpu=1), [device_id])[0]
    return dict(return_loss=False, rescale=True, **data)


def parse_args():
    parser = argparse.ArgumentParser(description='MMDet test detector')
    parser.add_argument('config', help='test config file path')
    parser.add_argument('checkpoint', help='checkpoint file')
    parser.add_argument(
        '--save_path', 
        type=str,
        help='path to save visual result')
    parser.add_argument(
        '--gpus', default=1, type=int, help='GPU number used for testing')
    parser.add_argument(
        '--proc_per_gpu',
        default=1,
        type=int,
        help='Number of processes per GPU')
    parser.add_argument('--out', help='output result file')
    parser.add_argument('--load_result', 
        action='store_true', 
        help='whether to load existing result')
    parser.add_argument(
        '--eval',
        type=str,
        nargs='+',
        choices=['bbox', 'segm'],
        help='eval types')
    parser.add_argument('--show', action='store_true', help='show results')

    ## Added. Customized command line arguments below.
    parser.add_argument('--test_mode', action='store_true', help='If enable, in test mode (just test infer fps).')
    parser.add_argument('--max_frame_count', type=int, default=1080,
        help='Only valid in test mode, the number of frames used to test. <=0 means all frame')
    parser.add_argument('--ann_file', help='Usually used in test mode. If on, use this as ann file path instead of that in config file.')
    parser.add_argument('--img_prefix', help='Usually used in test mode. If on, use this as image path instead of that in config file.')

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    if args.out is not None and not args.out.endswith(('.pkl', '.pickle')):
        raise ValueError('The output file must be a pkl file.')

    cfg = mmcv.Config.fromfile(args.config)
    # set cudnn_benchmark
    if cfg.get('cudnn_benchmark', False):
        torch.backends.cudnn.benchmark = True
    cfg.model.pretrained = None
    cfg.data.test.test_mode = True

    # Added. Reset the path to annotation and test images.
    if args.ann_file:
        cfg.data.test.ann_file = args.ann_file
    if args.img_prefix:
        cfg.data.test.img_prefix = args.img_prefix

    dataset = obj_from_dict(cfg.data.test, datasets, dict(test_mode=True))
    assert args.gpus == 1
    model = build_detector(
        cfg.model, train_cfg=None, test_cfg=cfg.test_cfg)
    load_checkpoint(model, args.checkpoint)
    model = MMDataParallel(model, device_ids=[0])

    data_loader = build_dataloader(
        dataset,
        imgs_per_gpu=1,
        workers_per_gpu=cfg.data.workers_per_gpu,
        num_gpus=1,
        dist=False,
        shuffle=False)
    if args.load_result:
        outputs = mmcv.load(args.out)
    else:
        max_frame_count = args.max_frame_count if args.test_mode else -1
        outputs = single_test(model, data_loader, args.show, save_path=args.save_path, max_frame_count=max_frame_count)

    # Added.
    # If test model, exit; otherwise, will fails.
    if args.test_mode:
        return

    if args.out:
        if not args.load_result:
          print('writing results to {}'.format(args.out))
        
          mmcv.dump(outputs, args.out)
        eval_types = args.eval
        if eval_types:
            print('Starting evaluate {}'.format(' and '.join(eval_types)))
            if not isinstance(outputs[0], dict):
                result_file = args.out + '.json'
                results2json_videoseg(dataset, outputs, result_file)
                ytvos_eval(result_file, eval_types, dataset.ytvos)
            else:
                NotImplemented

if __name__ == '__main__':
    main()
