
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apt-get -y update && \
    apt-get install -y ffmpeg git gcc libsndfile1 && \
    apt-get clean all && \
    rm -rf /var/cache/apt

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install git+https://github.com/m-bain/whisperx.git

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 8 --threads 8 --timeout 0 main:app