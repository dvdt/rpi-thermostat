#20210922 PSE: reordered imports per PEP-8 guidelines (https://www.python.org/dev/peps/pep-0008/#imports)
import collections
import queue
import sqlite3dbm
import conf

class ThermostatModes():
    AUTO = 'auto'
    MANUAL = 'manual'
    OFF = 'off'

#20210922 PSE: removed vestigial function get_ro_conn()

def get_conn():
    #20210922 PSE: added function definition docstring
    "Returns a sql database connection"
    return sqlite3dbm.sshelve.open(conf.SETPOINT_DB)


EVENT_QUEUE = queue.PriorityQueue()
TEMPERATURE_READINGS = collections.deque(maxlen=1 * 24 * 60)
HUMIDITY_READINGS = collections.deque(maxlen=1 * 24 * 60)

# Mode is initialized to AUTO.
CURRENT_MODE = ThermostatModes.AUTO