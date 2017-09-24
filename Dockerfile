FROM python:2.7-alpine
RUN apk add --no-cache git bash
RUN git clone https://github.com/UltimateHackers/XSStrike.git
WORKDIR /XSStrike/
RUN pip install -r requirements.txt
ENTRYPOINT ["python","xsstrike"]
