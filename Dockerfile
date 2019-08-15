FROM python:3.6

WORKDIR /app

ADD . /app

RUN pip install pipenv && pipenv install --system --deploy


EXPOSE 3000