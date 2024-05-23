# FROM alpine:3.17.3 
FROM python:latest
MAINTAINER bvt2202
WORKDIR /home
RUN mkdir src
# ENV PORT=
# ENV HOST=0.0.0.0

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
# RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY CasinoBackend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /home/src

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]