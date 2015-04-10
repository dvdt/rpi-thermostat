import sqlite3dbm
import Queue
SETPOINT_DB = 'temp_setpoints.sqlite3'

EVENT_QUEUE = Queue.PriorityQueue()
OVERRIDE_KEY = 'override'
# accesses the unix epoch for when the AC relay was last switched OFF
MOST_RECENT_OFF_KEY = 'most_recent_off'

# accesses the unix epoch for when the AC relay was last switched ON
MOST_RECENT_ON_KEY = 'most_recent_on'

def get_ro_conn():
    return sqlite3dbm.sshelve.open(SETPOINT_DB, 'r')

def get_conn():
    return sqlite3dbm.sshelve.open(SETPOINT_DB)

