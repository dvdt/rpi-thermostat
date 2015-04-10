# Raspberry Pi Home Thermostat

Install
---

```
virtualenv venv
source ./venv/bin/activate
pip install -r requirements.txt
sudo cp rpi-thermostat.conf /etc/supervisor/conf.d/
```

Deploy
---
```
./deploy
# in rpi
sudo supervisorctl reread
sudo supervisorctl update

# should be running now!
```

Run locally
---
```
python main.py

```

and then open [localhost:5000](localhost:5000) in a web browser.


