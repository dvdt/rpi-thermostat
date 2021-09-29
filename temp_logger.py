#!/usr/bin/python
#20210922 PSE: reordered imports per PEP-8 guidelines (https://www.python.org/dev/peps/pep-0008/#imports)
import logging
import requests
from apscheduler.schedulers.background import BlockingScheduler
import conf
try:
    import Adafruit_DHT
except ImportError as e:
    class Adafruit_DHTMOCK():
        def read_retry(self):
            return 25, 50
    Adafruit_DHT = Adafruit_DHTMOCK()

#20210922 PSE: global constant THERMOSTAT_URI was moved to conf, to reduce configuration points

def main():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, '17')
    if humidity is not None and temperature is not None:
        requests.post(conf.THERMOSTAT_URI, data=dict(temperature=temperature, humidity=humidity))
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

