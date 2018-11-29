FROM alpine:latest
MAINTAINER Furkan SAYIM <furkan.sayim@yandex.com>

ARG URL=""
ENV URL=${URL}

RUN apk update && \
    apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache && \
    apk add git

RUN git clone https://github.com/s0md3v/XSStrike.git

WORKDIR XSStrike

RUN pip3 install -r requirements.txt

CMD python3 xsstrike.py -u ${URL}
