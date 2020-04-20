FROM xshuden/alppython3
LABEL MAINTAINER furkan.sayim@yandex.com

RUN git clone --depth=1 'https://github.com/s0md3v/XSStrike.git' /tmp/xsstrike

WORKDIR /tmp/xsstrike
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "xsstrike.py"]
