# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster as base

WORKDIR /

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY movie_recs movie_recs

ENV FLASK_APP=movie_recs

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]

FROM base as debug
# Debug image reusing the base
# Install dev dependencies for debugging
RUN pip install debugpy
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1