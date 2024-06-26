FROM python:3.9

WORKDIR /code
 
COPY ./requirements.txt /code/requirements.txt

RUN apt update -y && apt install ffmpeg -y
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--port", "8080"]