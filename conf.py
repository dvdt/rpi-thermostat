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

# Name of setpoint database
SETPOINT_DB = 'temp_setpoints.sqlite3'

# Whether to return temperature values in Fahrenheit
FARENHEIT = True

# interval at which to run the event_handler function
EVENT_LOOP_INTERVAL = 60
# interval at which to run the bangbang_controller function
BANGBANG_LOOP_INTERVAL = 60

#20210922 PSE: moved to config from state - open to discussion for moving back to state,
#but this seemed like a more appropriate home

# how long to wait in seconds before alerting user that the readings are stale
STALE_READ_INTERVAL = 5 * 60
# accesses the unix epoch for when the AC relay was last switched OFF
MOST_RECENT_OFF_KEY = 'most_recent_off'
# accesses the unix epoch for when the AC relay was last switched ON
MOST_RECENT_ON_KEY = 'most_recent_on'
#20210922 PSE: moved to config from temp_logger to reduce configuration pain-points
THERMOSTAT_URI = 'http://192.168.1.214:5000/api/v1/temperature/'
