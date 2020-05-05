FROM juniper/pyez:2.4.1
ARG JSNAPY_HOME="/jsnapy"
ENV JSNAPY_HOME=$JSNAPY_HOME

LABEL maintainer="Stephen Steiner <ssteiner@juniper.net>"

WORKDIR /source

ADD setup.py . 
ADD requirements.txt . 
ADD lib lib
ADD tools tools
ADD logs logs

RUN apk add -q --no-cache git \
#    && pip3 -q --disable-pip-version-check install -r requirements.txt \
    && pip3 install . \
    && rm -rf /source

WORKDIR /usr/local/bin
ADD entrypoint.sh .
RUN chmod +x entrypoint.sh

WORKDIR $JSNAPY_HOME
VOLUME [$JSNAPY_HOME]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

