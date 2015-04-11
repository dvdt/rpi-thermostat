"""RESTful HTTP API for controlling a Raspberry Pi thermostat. API endpoints define setpoints for 8 3hr time intervals
throughout a 24hr day: 0-3, 3-6, 6-9, etc. Additionally, the user may override the scheduled setpoint for the next 3 hours.
Includes built-in hysteresis to avoid rapid on-off switching of HVAC systems; this hysteresis is not exposed in the API
for safety reasons.
"""

import flask
import flask.json
from flask import request
import logging
import time
import os
import rpi_relay
import state
import Queue
import werkzeug.exceptions

from apscheduler.schedulers.background import BackgroundScheduler

app = flask.Flask(__name__)


# Temperature setpoint is determined by the time of day, stored in SETPOINT_DB.
TEMP_SETPOINT_HOURS = (0, 3, 6, 9, 12, 15, 18, 21)

def get_request_db():
    "Returns a dbm database. Use only in a Flask app context!"
    db = getattr(flask.g, '_database', None)
    if db is None:
        # open a new connection as needed -- throughput doesn't need to be high for this!
        db = flask.g._database = state.get_ro_conn()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

def get_setpoint(hour):
    "Returns the temp setpoint for the given hour of day"
    ro_db = get_request_db()
    setpoint_key = [set_hr for set_hr in TEMP_SETPOINT_HOURS if hour >= set_hr][-1]
    return ro_db[setpoint_key]

def parse_setpoints(json_form):
    form = flask.json.loads(json_form['setpoints'])
    setpoints = {}

    for setpoint, val in form.iteritems():
        if isinstance(setpoint, basestring):
            setpoint = int(setpoint)
        if isinstance(val, basestring):
            val = int(val)
        if setpoint in TEMP_SETPOINT_HOURS:
            setpoints[setpoint] = val
        else:
            raise Exception("setpoint %s not valid" % setpoint)
    return setpoints

@app.route('/api/v1/setpoints/', methods=('POST', 'GET'))
def handle_setpoints_request():
    db = get_request_db()
    if request.method == 'POST':
        setpoints = parse_setpoints(request.form)
        print setpoints
        for hr, temp in setpoints.iteritems():
            db[hr] = temp
        return flask.json.jsonify(setpoints)

    if request.method == 'GET':
        setpoints = {hr: db.get(hr) for hr in TEMP_SETPOINT_HOURS}
        return flask.json.jsonify(setpoints)

@app.route('/api/v1/timer/', methods=('POST', 'GET'))
def handle_timer_request():
    'manual override for turning the AC on for a set amount of time.'
    def get_manual_status():
        if state.EVENT_QUEUE.queue:
            now = time.time()
            future_events = filter(lambda x: x[0] > now, state.EVENT_QUEUE.queue)
            if future_events:
                future_e, status = future_events[0]
                return flask.json.jsonify(dict(future_sec=(future_e - now), future_status=status))

        return flask.json.jsonify({})

    def handle_timer(on_time):
        if (on_time < rpi_relay.MIN_ON_TIME) or (on_time > rpi_relay.MAX_ON_TIME):
            raise werkzeug.exceptions.BadRequest(description='time_on exceeds valid params')
        turn_off_event = (time.time() + on_time, False)
        turn_on_event = (time.time(), True)
        new_queue = Queue.PriorityQueue()
        new_queue.put(turn_on_event)
        new_queue.put(turn_off_event)
        state.EVENT_QUEUE = new_queue

    if request.method == 'POST':
        on_time_int = int(request.form['on_time'])
        handle_timer(on_time_int)
        return get_manual_status()

    if request.method == 'GET':
        return get_manual_status()

def event_handler():
    logger = logging.getLogger('task_queue')
    q = state.EVENT_QUEUE
    conn = state.get_conn()
    try:
        exec_time, event = q.get(block=False)
        now = time.time()
        if now > exec_time:
            rpi_relay.set_ac_relay(event, conn)
            logger.info("setting relay=%s" % event)
        else:
            # put the event back into the queue if it isn't time to execute it yet
            q.put((exec_time, event))
        q.task_done()
    except Queue.Empty:
        pass

@app.route('/<path:path>/')
def resources(path):
    return flask.send_from_directory(STATIC_DIR, path)

@app.route('/')
def index():
    return flask.send_file('static/index.html')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s %(message)s')
    logger = logging.getLogger('main')

    STATIC_DIR = os.environ.get('STATIC_DIR', 'static')
    rpi_relay.init_RPi()
    scheduler = BackgroundScheduler()
    scheduler.start()

    scheduler.add_job(event_handler, 'interval', seconds=5)
    logger.info('starting scheduler')
    logger.info('starting web server')
    app.run(debug=False, host='0.0.0.0')
