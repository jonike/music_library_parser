FROM python:3.7-slim
MAINTAINER github.pdx

ENV PYTHONUNBUFFERED 1
COPY requirements.txt .

RUN apt-get update && \
  apt-get install -y --no-install-recommends build-essential && \
  pip install -r /requirements.txt && \
  apt-get purge -y build-essential && \
  apt-get autoremove -y && \
  apt-get autoclean -y && \
  rm -rf /var/lib/{apt, dpkg, cache,log} /tmp/* ~/.cache && \
  rm -rf /usr/src/python /usr/share/doc /usr/share/man && \
  rm -f /var/cache/apt/archives/*.deb

COPY ./data /data
COPY ./media_parser /media_parser
COPY ./tests /tests

WORKDIR /media_parser

RUN useradd user
USER user