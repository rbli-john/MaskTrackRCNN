container_name=rbli-masktrack-rcnn
image_name=rbli-masktrack-rcnn-image

docker stop ${container_name}
docker rm ${container_name}

nvidia-docker run -it --name ${container_name} -p 8891:8891 -u $(id -u):$(id -g) -v $HOME:$HOME -v /mnt/Data02:/mnt/Data02  -v /mnt/Backup:/mnt/Backup  -v /mnt/Backup2:/mnt/Backup2 -v /nfs/AI:/nfs/AI -v /nfs/SHARE/dataset/:/nfs/SHARE/dataset/ ${image_name} bash