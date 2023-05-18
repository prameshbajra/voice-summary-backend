FROM public.ecr.aws/lambda/python:3.10-arm64

RUN yum -y update && \
    yum -y install tar gzip xz && \
    yum clean all && \
    rm -rf /var/cache/yum

RUN curl https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz -o ffmpeg.tar.xz && \
    tar -xf ffmpeg.tar.xz && \
    mv ffmpeg-*-static/ffmpeg /usr/local/bin/ && \
    rm -r ffmpeg.tar.xz ffmpeg-*-static

COPY requirements.txt  .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY app/handler.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "handler.handler" ]
