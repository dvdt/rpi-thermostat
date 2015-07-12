# Raspberry pi GPIO pin controlling ac turn on relay
AC_RELAY_PIN = 12 # GPIO 18

# Temperature may drift +/- (HYSTERESIS_TEMP / 2) before changing AC state.
HYSTERESIS_TEMP = 3.0

# These parameters prevent rapid on/off cycling of the AC unit.
MIN_OFF_TIME = 5 * 60 # in seconds
MIN_ON_TIME = 5 * 60
MAX_ON_TIME = 2 * 60 * 60

# Temperature setpoint is determined by the time of day, stored in SETPOINT_DB.
TEMP_SETPOINT_HOURS = (0, 3, 6, 9, 12, 15, 18, 21)

SETPOINT_DB = 'temp_setpoints.sqlite3'

FARENHEIT = True

EVENT_LOOP_INTERVAL = 60
BANGBANG_LOOP_INTERVAL = 60