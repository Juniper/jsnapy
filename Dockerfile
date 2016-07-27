FROM juniper/pyez

#1 install jsnapy
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

#2 install  netconify
RUN pip install junos-netconify

#3 - Install ansible and Junos Galaxy module
RUN apk update \
    && apk upgrade \
    && apk add ansible \
    && ansible-galaxy install Juniper.junos

#4 - Clean up
RUN rm -rf /var/cache/apk/*

#5 Optional - Copy example files
#ADD ./example /tmp/example

