
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apt-get -y update && \
    apt-get install -y ffmpeg git gcc libsndfile1 && \
    apt-get clean all && \
    rm -rf /var/cache/apt && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt && \
    pip install git+https://github.com/m-bain/whisperx.git

