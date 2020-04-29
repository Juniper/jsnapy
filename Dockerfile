FROM juniper/pyez:2.4.1

WORKDIR /source

#1 Copy project inside the container
ADD setup.py setup.py
ADD requirements.txt requirements.txt
ADD lib lib
ADD tools tools
ADD samples samples
ADD logs logs
ADD testfiles testfiles
ADD snapshots snapshots

#2 Install netconify install Ansible + Junos module
# Install Jsnapy from source
# Clean up everything
RUN apk add -q --no-cache git \
    && pip3 -q --disable-pip-version-check install -r requirements.txt \
    && ansible-galaxy install Juniper.junos \
    && pip3 install . \
    && rm -rf /source

WORKDIR /scripts

VOLUME [/script]

ENTRYPOINT ["/usr/bin/jsnapy"]

