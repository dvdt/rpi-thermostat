# Raspberry Pi Home Thermostat

Install
---

```
sudo apt-get install python-pip
sudo apt-get install supervisor
sudo pip install virtualenv
virtualenv venv
source ./venv/bin/activate
pip install -r requirements.txt
sudo cp rpi-thermostat.conf /etc/supervisor/conf.d/
sudo cp temp_logger.conf /etc/supervisor/conf.d/
```

also make sure to install [DHT22 software from adafruit](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/overview)

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


