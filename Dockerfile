FROM public.ecr.aws/lambda/python:3.10-arm64


COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY app/handler.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "handler.handler" ] 




# Use public ECR AWS Lambda Python image
# FROM public.ecr.aws/lambda/python:3.10-arm64

# # Download and install ffmpeg
# RUN yum -y update && \
#     yum -y install tar gzip && \
#     curl https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz -o ffmpeg.tar.xz && \
#     tar -xf ffmpeg.tar.xz && \
#     rm ffmpeg.tar.xz && \
#     mv ffmpeg-*-static/ffmpeg /usr/local/bin/ && \
#     rm -r ffmpeg-*-static

# # Copy requirements and install dependencies
# COPY requirements.txt  .
# RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# # Copy function code
# COPY app/handler.py ${LAMBDA_TASK_ROOT}

# # Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
# CMD [ "handler.handler" ] 
