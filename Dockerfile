FROM juniper/pyez:2.4.1

WORKDIR /source

ADD setup.py setup.py
ADD requirements.txt requirements.txt
ADD lib lib
ADD tools tools
ADD logs logs

RUN apk add -q --no-cache git \
    && pip3 -q --disable-pip-version-check install -r requirements.txt \
    && ansible-galaxy install Juniper.junos \
    && pip3 install . \
    && rm -rf /source

WORKDIR /usr/local/bin
ADD entrypoint.sh .
RUN chmod +x entrypoint.sh

WORKDIR /scripts
VOLUME [/scripts]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

