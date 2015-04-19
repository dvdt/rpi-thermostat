#!/usr/bin/python

import Adafruit_DHT
import requests
import logging
import json
THERMOSTAT_URI = 'http://192.168.1.214:5000/api/v1/temperature/'

def main():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, '18')
    if humidity is not None and temperature is not None:
        requests.post(THERMOSTAT_URI, data=dict(temperature=temperature, humidity=humidity))
        logger.info('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        logger.error('Failed to get reading. Try again!')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s %(message)s')
    logger = logging.getLogger('main')
    main()