from collections import defaultdict
import logging
import time
from state import MOST_RECENT_ON_KEY, MOST_RECENT_OFF_KEY
import conf
try:
    import RPi.GPIO as GPIO
except ImportError, e:
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


def can_turn_on(current_epoch_time, db):
    last_off_epoch = db.get(MOST_RECENT_OFF_KEY)
    logging.debug(last_off_epoch)
    if (last_off_epoch is None) or (current_epoch_time - last_off_epoch) > conf.MIN_OFF_TIME:
        return True
    else:
        logging.warn('cannot turn on')
    return False

def can_turn_off(current_epoch_time, db):
    last_on_epoch = db.get(MOST_RECENT_ON_KEY)
    if (last_on_epoch is None) or (current_epoch_time - last_on_epoch) > conf.MIN_ON_TIME:
        return True
    else:
        logging.warn('cannot turn off')
    return False

def init_RPi():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(conf.AC_RELAY_PIN, GPIO.OUT)

# Low level controls
def _set_ac_on(db):
    "Turns relay to high, turning on the AC"
    if can_turn_on(time.time(), db):
        GPIO.output(conf.AC_RELAY_PIN, True)
        db[MOST_RECENT_ON_KEY] = time.time()
        logging.warn("turned AC on")

def _set_ac_off(db):
    "Turns relay to low, turning off the AC"
    if can_turn_off(time.time(), db):
        GPIO.output(conf.AC_RELAY_PIN, False)
        db[MOST_RECENT_OFF_KEY] = time.time()
        logging.warn("turned AC off")

def set_ac_relay(status, conn):
    if bool(status) is True:
        _set_ac_on(conn)
    elif bool(status) is False:
        _set_ac_off(conn)
    else:
        raise ValueError("invalid status")

def ac_status():
    return bool(GPIO.input(conf.AC_RELAY_PIN))