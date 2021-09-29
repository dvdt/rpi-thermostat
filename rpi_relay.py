from collections import defaultdict
import logging
import time
import conf
try:
    import RPi.GPIO as GPIO
except ImportError as e:
    # logging.warn("unable to find RPi.GPIO!!")
    class GPIOMock():
        BOARD = None
        OUT = None

        def __init__(self):
            self.status = defaultdict(int)

        def setmode(self, *args):
            pass

        def setup(self, *args):
            pass

        def input(self, pin):
            logging.warn("using mock gpio")
            return self.status[pin]

        def output(self, pin, s):
            logging.warn("setting pin=%d to %s" % (pin, s))
            self.status[pin] = s
    GPIO = GPIOMock()


def _can_turn(db, current_epoch_time, recent_key, min_time, status):
    # 20210922 PSE: combined _can_turn_on and _can_turn_off into single function to avoid code duplication
    # 20210922 PSE: added function definition
    "Returns boolean whether the device can be turned on or off"
    last_epoch = db.get(recent_key)
    if (last_epoch is None) or (current_epoch_time - last_epoch) > min_time:
        return True
    logging.warn(f'cannot turn {"on" if status else "off"}')
    return False

def init_RPi():
    # 20210922 PSE: added function definition
    "Returns None: initializes RPi"
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(conf.AC_RELAY_PIN, GPIO.OUT)

def _set_ac(db, status):
    # 20210922 PSE: combined set_ac_on and set_ac_off into single function to avoid code duplication
    # 20210922 PSE: added function definition
    "Returns None: turns the AC on or off, depending on ac_relay"
    if status:
        recent_key = conf.MOST_RECENT_OFF_KEY
        min_time = conf.MIN_OFF_TIME
        set_key = conf.MOST_RECENT_ON_KEY
    else:
        recent_key = conf.MOST_RECENT_ON_KEY
        min_time = conf.MIN_ON_TIME
        set_key = conf.MOST_RECENT_OFF_KEY
    if _can_turn(db, time.time(), recent_key, min_time, status):
        GPIO.output(conf.AC_RELAY_PIN, status)
        db[set_key] = time.time()
        logging.warn(f'turned AC {"on" if status else "off"}')

def set_ac_relay(status, conn):
    # 20210922 PSE: added function definition
    "Returns None: sets ac relay based on status"
    if isinstance(bool(status), bool):
        _set_ac(conn, bool(status))
    else:
        raise ValueError("invalid status")

def ac_status():
    # 20210922 PSE: added function definition
    "Returns bool AC_RELAY_PIN status"
    return bool(GPIO.input(conf.AC_RELAY_PIN))