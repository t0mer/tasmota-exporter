import requests
import sys
import signal
from os import getenv
from time import sleep
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
from loguru import logger

class TasmotaCollector(object):
    def __init__(self):
        self.ip = getenv('DEVICE_IP')
        self.device_name = getenv("DEVICE_NAME").lower()
        self.user = getenv('USER')
        self.password = getenv('PASSWORD')

    def collect(self):

        response = self.fetch()

        for key in response:
            metric_name =  self.device_name +  "_" + key.lower().replace(" ", "_") 
            metric = response[key].split()[0]
            unit = None
            if len(response[key].split()) > 1:
                unit = response[key].split()[1]

            if "today" in metric_name or "yesterday" in metric_name or "total" in metric_name:
                r = CounterMetricFamily(metric_name, key, labels=['device'], unit=unit)
            else:
                r = GaugeMetricFamily(metric_name, key, labels=['device'], unit=unit)
            r.add_metric([self.ip], metric)
            yield r

    def fetch(self):

        url = 'http://' + self.ip + '/?m=1'
        logger.info("Getting Metrics from: " + url)
        session = requests.Session()
        

        if self.user and self.password:
            session.auth = (self.user, self.password)

        page = session.get(url)

        values = {}
        
        string_values = str(page.text).split("{s}")
        for i in range(1,len(string_values)):
            label = string_values[i].split("{m}")[0]
            value = string_values[i].split("{m}")[1].split("{e}")[0]
            values[label] = value

        return values

def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':

    port = 8000

    start_http_server(int(port))
    REGISTRY.register(TasmotaCollector())

    while(True):
        sleep(1)
    
