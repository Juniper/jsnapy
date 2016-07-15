FROM ubuntu:14.04

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y wget build-essential libwrap0-dev libssl-dev \
         python-distutils-extra libc-ares-dev uuid-dev python-pip \
         python-dev libxml2-dev libxslt1-dev libffi-dev ansible libyaml-dev

#1 install Pyez & update distribute package
RUN pip install -U ncclient junos-eznc distribute

#2 install jsnapy
RUN mkdir -p /usr/local/tmp/jsnapy
ADD lib /usr/local/tmp/jsnapy/lib
ADD logs /usr/local/tmp/jsnapy/logs
ADD MANIFEST.in /usr/local/tmp/jsnapy/MANIFEST.in
ADD requirements.txt /usr/local/tmp/jsnapy/requirements.txt
ADD samples /usr/local/tmp/jsnapy/samples
ADD setup.py /usr/local/tmp/jsnapy/setup.py
ADD snapshots /usr/local/tmp/jsnapy/snapshots
ADD testfiles /usr/local/tmp/jsnapy/testfiles
ADD tools /usr/local/tmp/jsnapy/tools
WORKDIR /usr/local/tmp/jsnapy
RUN python setup.py sdist
RUN pip install dist/jsnapy-0.1.tar.gz

#3 install  netconify
RUN pip install junos-netconify

#4 - Install Junos Galaxy on ansible
RUN ansible-galaxy install Juniper.junos

#5 - Clean up
RUN apt-get clean &&\
apt-get purge

#6 Optional - Copy example files
#ADD ./example /tmp/example
