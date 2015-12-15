FROM phusion/baseimage:0.9.17
MAINTAINER Damien Garros <dgarros@gmail.com>

RUN apt-get -y update && \
    apt-get -y upgrade

RUN apt-get install -y wget build-essential libwrap0-dev libssl-dev python-distutils-extra libc-ares-dev uuid-dev
RUN apt-get install -y python-pip python-dev libxml2-dev libxslt1-dev
RUN pip install junos-eznc
RUN mkdir -p /usr/local/tmp/jsnapy
ADD jsnapy /usr/local/tmp/jsnapy
WORKDIR /usr/local/tmp/jsnapy

RUN python setup.py sdist
RUN pip install dist/jsnapy-0.1.tar.gz
