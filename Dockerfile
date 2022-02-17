# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

WORKDIR /

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY movie_recs movie_recs

ENV FLASK_APP=movie_recs

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]