# syntax=docker/dockerfile:1
FROM python:alpine AS build-env

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 --no-cache-dir install -r requirements.txt --target /packages

COPY app.py app.py
COPY run.py run.py

FROM gcr.io/distroless/python3-debian13:latest

COPY --from=build-env /app /app
COPY --from=build-env /packages /packages

ENV PYTHONPATH=/packages

WORKDIR /app

CMD ["run.py"]