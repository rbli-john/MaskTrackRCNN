CUDA_VISIBLE_DEVICES=1 python tools/test_video.py \
    configs/masktrack_rcnn_r50_fpn_1x_youtubevos.py \
    /home/us000110/codebases/models_pretrained/GitHub/MaskTrackRCN/epoch_12.pth \
    --out output/result.pkl --eval segm \
    --test_mode \
    --max_frame_count 1080 \
    --ann_file /nfs/AI/SegDepth/data/vis/annotations/valid.json \
    --img_prefix /nfs/AI/SegDepth/data/vis/valid/JPEGImages
