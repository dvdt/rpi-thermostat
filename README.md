# Raspberry Pi Home Thermostat

Install
---

[configure wifi](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md)

```
sudo apt-get install python-pip
sudo apt-get install supervisor
sudo pip install virtualenv
virtualenv venv
source ./venv/bin/activate
pip install -r requirements.txt
```


thermostat relay specific
```
sudo cp rpi-thermostat.conf /etc/supervisor/conf.d/
```

temp logger specific

```{python}
sudo cp temp_logger.conf /etc/supervisor/conf.d/
# install [DHT22 software from adafruit](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/overview)
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
sudo apt-get update
sudo apt-get install build-essential python-dev
cd Adafruit_Python_DHT && sudo python setup.py install
```



Deploy
---
```
./deploy
# in rpi
sudo supervisorctl reread
sudo supervisorctl restart thermostat
sudo supervisorctl restart temp_logger

# should be running now!
```

Run locally
---
```
python main.py

```

and then open [localhost:5000](localhost:5000) in a web browser.


