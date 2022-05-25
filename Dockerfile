FROM python:3.10-slim-buster

LABEL maintainer="peto.kajan@gmail.com" \
      description="Script extracting relevant data (emails, facebook, product info...) from domains read from input file "

# Set environment for python
ENV PYTHONNOUSERSITE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=1

# This is the base requirements set
RUN apt-get -y update \
    && apt-get -y --no-install-recommends install bash curl jq make \
    && apt-get -y clean
COPY requirements.txt /app/
WORKDIR /app

# Create virtualenv and install requirements
RUN apt-get -y --no-install-recommends install build-essential \
    && pip install \
        --no-cache-dir \
        --upgrade pip cython  \
        -r requirements.txt \
    && apt-get -y remove --purge build-essential \
    && apt-get -y autoremove --purge \
    && apt-get -y clean

COPY . /app/

ENTRYPOINT ["python","./main.py"]
