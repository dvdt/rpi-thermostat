from collections import defaultdict

try:
    import RPi.GPIO as GPIO
except ImportError, e:
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
            return self.status[pin]

        def output(self, pin, s):
            self.status[pin] = s
    GPIO = GPIOMock()


import logging; logger = logging.getLogger(__name__)
import time
import state
from state import MOST_RECENT_ON_KEY, MOST_RECENT_OFF_KEY

AC_RELAY_PIN = 12

# Temperature may drift +/- (HYSTERESIS_TEMP / 2) before changing AC state.
HYSTERESIS_TEMP = 10

# These parameters prevent rapid on/off cycling of the AC unit.
MIN_OFF_TIME = 30 * 60 # in seconds
MIN_ON_TIME = 10 * 60
MAX_ON_TIME = 2 * 60 * 60



def can_turn_on(current_epoch_time, db):
    last_off_epoch = db.get(MOST_RECENT_OFF_KEY)
    if (last_off_epoch is None) or (current_epoch_time - last_off_epoch) > MIN_OFF_TIME:
        return True
    return False

def can_turn_off(current_epoch_time, db):
    last_on_epoch = db.get(MOST_RECENT_ON_KEY)
    if (last_on_epoch is None) or (current_epoch_time - last_on_epoch) > MIN_ON_TIME:
        return True
    return False

def init_RPi():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(AC_RELAY_PIN, GPIO.OUT)

# Low level controls
def _set_ac_on(db):
    "Turns relay to high, turning on the AC"
    if (GPIO.input(AC_RELAY_PIN) is False) and can_turn_on(time.time(), db):
        GPIO.output(AC_RELAY_PIN, True)
        db[MOST_RECENT_ON_KEY] = time.time()
        logger.info("turned AC on")

def _set_ac_off(db):
    "Turns relay to low, turning off the AC"
    if (GPIO.input(AC_RELAY_PIN) is True) and can_turn_off(time.time(), db):
        GPIO.output(AC_RELAY_PIN, False)
        db[MOST_RECENT_OFF_KEY] = time.time()
        logger.info("turned AC off")

def set_ac_relay(status, conn):
    if bool(status) is True:
        _set_ac_on(conn)
    elif bool(status) is False:
        _set_ac_off(conn)
    else:
        raise ValueError("invalid status")

def ac_status():
    return bool(GPIO.input(AC_RELAY_PIN))