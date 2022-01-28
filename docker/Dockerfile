FROM ufoym/deepo:all-jupyter-py36-cu100
ENV http_proxy=http://172.24.206.4:3128
ENV https_proxy=http://172.24.206.4:3128
RUN apt-get update -qq   && apt-get install -y -qq python3 libglu1-mesa-dev ffmpeg

RUN pip install pytorch=0.4.1 torchvision cuda92
&& pip install cudatoolkit-dev=9.2
&& pip install opencv-python
&& pip install cython
&& pip install git+https://github.com/youtubevos/cocoapi.git#"egg=pycocotools&subdirectory=PythonAPI"

RUN bash compile.sh
RUN pip install .

WORKDIR /home/us000110

RUN groupadd -g 10000 oppous \
&& useradd -g oppous -u 1000110 us000110
