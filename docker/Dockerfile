# Using cu100 will meets CUDA error: invalid device function. Possibly,cu100 has some inconsistency with cu11.4 GPU.
FROM ufoym/deepo:all-py36-cu101
ENV http_proxy=http://172.24.206.4:3128
ENV https_proxy=http://172.24.206.4:3128
RUN apt-get update -qq   && apt-get install -y -qq python3 libglu1-mesa-dev ffmpeg

# Do NOT use pytorch version larger than 1.5.
RUN pip install --upgrade pip \
&& pip install torch==1.4.0 torchvision==0.5.0 \   
&& pip install opencv-python \
&& pip install cython \
&& pip install git+https://github.com/youtubevos/cocoapi.git#"egg=pycocotools&subdirectory=PythonAPI"

# Before is for user specific. Change user/group name/id according to your case.
WORKDIR /home/us000110

RUN groupadd -g 10000 oppous \
&& useradd -g oppous -u 1000110 us000110
