FROM python:3.9-slim-buster

LABEL maintainer="pmshireen@gmail.com"

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=main.py

CMD ["flask", "run", "--host", "0.0.0.0"]
