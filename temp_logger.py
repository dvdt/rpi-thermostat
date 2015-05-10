#!/usr/bin/python

try:
    import Adafruit_DHT
except ImportError, e:
    class Adafruit_DHTMOCK():
        def read_retry(self):
            return 25, 50
    Adafruit_DHT = Adafruit_DHTMOCK()
import requests
import logging
from apscheduler.schedulers.background import BlockingScheduler

THERMOSTAT_URI = 'http://192.168.1.214:5000/api/v1/temperature/'

def main():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, '17')
    if humidity is not None and temperature is not None:
        requests.post(THERMOSTAT_URI, data=dict(temperature=temperature, humidity=humidity))
        logger.warn('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        logger.error('Failed to get reading. Try again!')

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN, format='%(levelname)s - %(asctime)s %(message)s')
    logger = logging.getLogger('main')
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'interval', seconds=60)
    logger.warn('starting scheduler')
    scheduler.start()

