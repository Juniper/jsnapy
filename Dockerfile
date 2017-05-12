FROM juniper/pyez:2.0.1

RUN rm -rf /source \
    && mkdir /source

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
RUN apk update \
    && apk add git ansible \
    && ansible-galaxy install Juniper.junos \
    && pip install -r requirements.txt \
    && pip install . \
    && rm -rf /var/cache/apk/* \
    && rm -rf /source

WORKDIR /scripts

VOLUME ["$PWD:/scripts"]

#ENTRYPOINT "/bin/ash"
