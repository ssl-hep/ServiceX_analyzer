FROM python:3.6
MAINTAINER Ben Galewsky

# Install vi to make debugging easier
RUN apt-get update && \
    apt-get install vim -y

RUN mkdir /servicex
COPY requirements.txt /servicex

RUN pip install -r /servicex/requirements.txt

COPY . /servicex/
