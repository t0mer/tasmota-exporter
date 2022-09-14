FROM python:alpine
RUN apk add --no-cache tini

ADD metrics.py /metrics.py
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ENV DEVICE_NAME "tasmota"
ENV DEVICE_IP "192.168.4.1"
ENV USER ""
ENV PASSWORD ""

EXPOSE 8000

RUN mkdir /app
COPY metrics.py /app

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python" , "/app/metrics.py"]