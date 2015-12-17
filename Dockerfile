FROM ubuntu:14.04

RUN apt-get -y update && \
    apt-get -y upgrade

RUN apt-get install -y wget build-essential libwrap0-dev libssl-dev python-distutils-extra libc-ares-dev uuid-dev
RUN apt-get install -y python-pip python-dev libxml2-dev libxslt1-dev

#1 install Pyez
RUN pip install ncclient
RUN pip install junos-eznc

#2 install jsnapy 
RUN mkdir -p /usr/local/tmp/jsnapy
ADD lib /usr/local/tmp/jsnapy/lib
ADD setup.py /usr/local/tmp/jsnapy/setup.py
ADD tests /usr/local/tmp/jsnapy/tests
ADD MANIFEST.in /usr/local/tmp/jsnapy/MANIFEST.in
ADD requirements.txt /usr/local/tmp/jsnapy/requirements.txt
ADD snapshots /usr/local/tmp/jsnapy/snapshots
WORKDIR /usr/local/tmp/jsnapy
RUN python setup.py sdist
RUN pip install dist/jsnapy-0.1.tar.gz

#3 install  netconify
RUN pip install junos-netconify

#4 Install Ansible
RUN mkdir -p /etc/ansible
RUN pip install ansible 

#5 - Install Junos Galaxy on ansible
RUN ansible-galaxy install Juniper.junos

#6 - Clean up
RUN apt-get clean &&\ 
apt-get purge

#7 Optional - Copy example files
#ADD ./example /tmp/example
