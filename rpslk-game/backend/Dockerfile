# syntax=docker/dockerfile:1
FROM python:3.15.0a2-slim AS build-env

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 --no-cache-dir install -r requirements.txt --target /packages

COPY app.py app.py
COPY run.py run.py

FROM gcr.io/distroless/python3

WORKDIR /app
COPY --from=build-env /app /app
COPY --from=build-env /packages /packages

ENV PYTHONPATH=/packages

CMD ["run.py"]
