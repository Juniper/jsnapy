FROM juniper/pyez:2.0.1

#1 Install git and netconify, and install Ansible + Junos module
RUN apk update \
    && apk add git ansible \
    && ansible-galaxy install Juniper.junos \
    && pip install junos-netconify

#2 install jsnapy release 1.0.0 from Github
WORKDIR /tmp/jsnapy
RUN pip install git+https://github.com/Juniper/jsnapy.git

#4 - Clean up
RUN rm -rf /var/cache/apk/* \
    && rm -rf /tmp/jsnapy

#5 Optional - Copy example files
#ADD ./example /tmp/example

ENTRYPOINT "/bin/ash"
