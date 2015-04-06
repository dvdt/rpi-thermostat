"""RESTful HTTP API for controlling a Raspberry Pi thermostat. API endpoints define setpoints for 8 3hr time intervals
throughout a 24hr day: 0-3, 3-6, 6-9, etc. Additionally, the user may override the scheduled setpoint for the next 3 hours.
Includes built-in hysteresis to avoid rapid on-off switching of HVAC systems; this hysteresis is not exposed in the API
for safety reasons.
"""

import flask
import flask.json
from flask import request
import sqlite3dbm
import threading
from datetime import datetime
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler

app = flask.Flask(__name__)

SETPOINT_DB = 'temp_setpoints.sqlite3'

# Temperature setpoint is determined by the time of day, stored in SETPOINT_DB.
TEMP_SETPOINT_HOURS = (0, 3, 6, 9, 12, 15, 18, 21)

def get_request_db():
    "Returns a dbm database. Use only in a Flask app context!"
    db = getattr(flask.g, '_database', None)
    if db is None:
        # open a new connection as needed -- throughput doesn't need to be high for this!
        db = flask.g._database = sqlite3dbm.sshelve.open(SETPOINT_DB)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

def get_setpoint(hour):
    "Returns the temp setpoint for the given hour of day"
    ro_db = sqlite3dbm.sshelve.open(SETPOINT_DB, flag='r')
    setpoint_key = [set_hr for set_hr in TEMP_SETPOINT_HOURS if hour >= set_hr][-1]
    return ro_db[setpoint_key]

def print_state():
    print "gettung setpoint: %s" % get_setpoint(0)

def parse_setpoints(json_form):
    form = flask.json.loads(json_form)
    setpoints = {}

    for setpoint, val in form.iteritems():
        if setpoint in TEMP_SETPOINT_HOURS:
            assert isinstance(val, int)
            assert 0 <= val < 24
            setpoints[setpoint] = val
    return setpoints

@app.route('/api/v1/setpoints/', methods=('POST', 'GET'))
def handle_setpoints_request():
    db = get_request_db()
    if request.method == 'POST':
        setpoints = parse_setpoints(request.form)

    if request.method == 'GET':
        setpoints = {hr: db.get(hr) for hr in TEMP_SETPOINT_HOURS}
        return flask.json.jsonify(setpoints)

@app.route('/<path:path>/')
def resources(path):
    return flask.send_from_directory('static', path)

@app.route('/')
def index():
    return flask.send_file('static/index.html')


if __name__ == '__main__':
    WRITE_DB = sqlite3dbm.sshelve.open(SETPOINT_DB)
    scheduler = BackgroundScheduler()
    scheduler.add_job(print_state, 'interval', seconds=3)
    # scheduler.start()
    app.run(debug=True)
