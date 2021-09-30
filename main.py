"""RESTful HTTP API for controlling a Raspberry Pi thermostat. API endpoints define setpoints for 8 3hr time intervals
throughout a 24hr day: 0-3, 3-6, 6-9, etc. Additionally, the user may override the scheduled setpoint for the next 3 hours.
Includes built-in hysteresis to avoid rapid on-off switching of HVAC systems; this hysteresis is not exposed in the API
for safety reasons.
"""
#20210922 PSE: reordered imports per PEP-8 guidelines (https://www.python.org/dev/peps/pep-0008/#imports)
#20210922 PSE: collections never accessed, removed from import
import datetime
import logging
import os
import queue
import time
from apscheduler.schedulers.background import BackgroundScheduler
import flask
import flask.json
from flask import request
import werkzeug.exceptions
import conf
import rpi_relay
import state



app = flask.Flask(__name__)


#20210922 PSE: global constant TEMP_SETPOINT_HOURS was duplicated in conf, which should be source of truth;
#removed duplicate declaration.

def _get_request_db():
    "Returns a dbm database. Use only in a Flask app context!"
    db = getattr(flask.g, '_database', None)
    if db is None:
        # open a new connection as needed -- throughput doesn't need to be high for this!
        db = flask.g._database = state.get_conn()
    return db

def _to_farenheit(c):
    #20210922 PSE: added function definition docstring
    "Returns a fahrenheit equivalent given a celcius measurement"
    return 9.0/5.0 * c + 32

def _get_setpoint(hour, db=None):
    "Returns the temp setpoint for the given hour of day"
    if db is None:
        db = _get_request_db()
    setpoint_key = [set_hr for set_hr in conf.TEMP_SETPOINT_HOURS if hour >= set_hr][-1]
    return db[setpoint_key]

def _parse_setpoints(json_form):
    "Returns a formatted list of setpoints from a POST request payload"
    form = flask.json.loads(json_form['setpoints'])
    setpoints = {}
    for setpoint, val in form.iteritems():
        #20210922 PSE: changed basestring to str for python 3 compatibility
        if isinstance(setpoint, str):
            setpoint = int(setpoint)
        if isinstance(val, str):
            val = float(val)
        if setpoint in conf.TEMP_SETPOINT_HOURS:
            setpoints[setpoint] = val
        else:
            raise Exception(f'setpoint {setpoint} not valid')
    return setpoints

#20210922 PSE: moved _event_handler to top, to organize @app route calls
def _event_handler():
    "Returns None - main event handler for events inside STATE queue"
    logger = logging.getLogger('task_queue')
    q = state.EVENT_QUEUE
    conn = state.get_conn()
    try:
        exec_time, event = q.get(block=False)
        now = time.time()
        if now > exec_time:
            rpi_relay.set_ac_relay(event, conn)
            logger.info(f'setting relay={event}')
        else:
            # put the event back into the queue if it isn't time to execute it yet
            q.put((exec_time, event))
        q.task_done()
    except queue.Empty:
        pass

#20210922 PSE: moved bangbang_controller to top, to organize @app route calls
def _bangbang_controller():
    #20210922 PSE: added function definition docstring
    "Returns None - main equipment controller"
    def is_stale(timestamp):
        #20210922 PSE: added function definition docstring
        "Returns bool whether the last reading has passed the STALE_READ_INTERVAL threshold"
        if time.time() - int(timestamp) > conf.STALE_READ_INTERVAL:
            return True
        return False

    logger = logging.getLogger('bangbang_controller')

    if state.CURRENT_MODE != state.ThermostatModes.AUTO:
        logger.warn(f'mode is set to {state.CURRENT_MODE}')
        return

    conn = state.get_conn()
    temp_read_time, most_recent_temp = state.TEMPERATURE_READINGS[-1]
    #20210922 PSE: removed unused variable most_recent_humidity
    humid_read_time = state.HUMIDITY_READINGS[-1][0]

    if is_stale(temp_read_time) or is_stale(humid_read_time):
        state.CURRENT_MODE = state.ThermostatModes.MANUAL
        logger.error('temperature readings are stale! setting mode to MANUAL')
        return

    now = datetime.datetime.now()
    current_setpoint = _get_setpoint(now.hour, db=conn)

    #20210922 PSE: refactored to compress into single if loop, avoid repetitive code
    turn_on = True if most_recent_temp > current_setpoint else False
    if abs(most_recent_temp - current_setpoint) > (conf.HYSTERESIS_TEMP / 2.0):
        turn_event = (time.time(), turn_on)
        state.EVENT_QUEUE.put(turn_event)
        if rpi_relay.ac_status() != turn_on:
            logger.warn(f'Temp={most_recent_temp}, setpoint={current_setpoint}, Setting AC {"ON" if turn_on else "OFF"}')

#20210922 PSE: moved close_connection down to organize @app route calls
@app.teardown_appcontext
def close_connection(exception):
    "Returns None: flask call handler to close database connection"
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

@app.route('/api/v1/setpoints/', methods=('POST', 'GET'))
def handle_setpoints_request():
    #20210922 PSE: added function definition docstring
    "Returns a JSON object of setpoints after a GET or POST request"
    db = _get_request_db()
    if request.method == 'POST':
        setpoints = _parse_setpoints(request.form)
        for hr, temp in setpoints.iteritems():
            db[hr] = temp
    #20210922 PSE: removed duplicate return statement, de-dented second
    if request.method == 'GET':
        setpoints = {hr: db.get(hr) for hr in conf.TEMP_SETPOINT_HOURS}
    return flask.json.jsonify(setpoints)

@app.route('/api/v1/status/', methods=('GET',))
def return_relay_status():
    #20210922 PSE: added function definition docstring
    "Returns a JSON object of setpoints after a GET request"
    return flask.json.jsonify({'ac_on': rpi_relay.ac_status()})

@app.route('/api/v1/mode/', methods=('GET', 'POST'))
def handle_thermostat_mode():
    #20210922 PSE: added function definition docstring
    "Returns a JSON object of current mode after a GET or POST request"
    #20210922 PSE: removed GET method loop, since it was not needed after return statement was de-dented
    if request.method == 'POST':
        mode = request.form.get('mode')
        assert mode in [state.ThermostatModes.AUTO, state.ThermostatModes.MANUAL, state.ThermostatModes.OFF]
        state.CURRENT_MODE = mode
    return flask.json.jsonify({'mode': state.CURRENT_MODE})

@app.route('/api/v1/temperature/', methods=('POST', 'GET'))
def handle_temp():
    #20210922 PSE: added function definition docstring
    "Returns a JSON object of current mode after a GET request"
    logger.info('in temperature')
    if request.method == 'POST':
        logger.warn(request.form)
        temp = float(request.form.get('temperature'))
        if conf.FARENHEIT is True:
            temp = _to_farenheit(temp)
        humidity = float(request.form.get('humidity'))
        logger.warn(f'temp={temp}, humidity={humidity}')
        now = time.time()
        state.TEMPERATURE_READINGS.append((now, temp))
        state.HUMIDITY_READINGS.append((now, humidity))
    #20210922 PSE: Removed GET loop and returned temperatures and humidities for either GET or POST.
    #This was for standardization; this was the only POST request that returned a string, rather than
    #an object
    temperatures = [x for x in state.TEMPERATURE_READINGS]
    humidities = [x for x in state.HUMIDITY_READINGS]
    return flask.json.jsonify(dict(temperature=temperatures, humidity=humidities))

@app.route('/api/v1/timer/', methods=('POST', 'GET'))
def handle_timer_request():
    #20210922 PSE: Standardized function definition docstring
    "manual override for turning the AC on for a set amount of time."
    def get_manual_status():
        #20210922 PSE: added function definition docstring
        "Returns dictionary of events inside the EVENT_QUEUE"
        if state.EVENT_QUEUE.queue:
            now = time.time()
            future_events = filter(lambda x: x[0] > now, state.EVENT_QUEUE.queue)
            if future_events:
                future_e, status = future_events[0]
                return flask.json.jsonify(dict(future_sec=(future_e - now), future_status=status))

        return flask.json.jsonify({})

    def handle_timer(on_time):
        #20210922 PSE: added function definition docstring
        "Returns None: replaces entire EVENT_QUEUE with a turn-on time and turn-off time"
        if (on_time < conf.MIN_ON_TIME) or (on_time > conf.MAX_ON_TIME):
            raise werkzeug.exceptions.BadRequest(description='time_on exceeds valid params')
        turn_off_event = (time.time() + on_time, False)
        turn_on_event = (time.time(), True)
        new_queue = queue.PriorityQueue()
        new_queue.put(turn_on_event)
        new_queue.put(turn_off_event)
        state.EVENT_QUEUE = new_queue

    if request.method == 'POST':
        on_time_int = int(request.form['on_time'])
        handle_timer(on_time_int)

    #20210922 PSE: removed GET method loop, since it was not needed after return statement was de-dented
    return get_manual_status()

@app.route('/<path:path>/')
def resources(path):
    #20210922 PSE: added function definition docstring
    "Returns flask path"
    return flask.send_from_directory(STATIC_DIR, path)

@app.route('/')
def index():
    #20210922 PSE: added function definition docstring
    "Returns index.html"
    return flask.send_file('static/index.html')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s %(message)s')
    logger = logging.getLogger('main')

    STATIC_DIR = os.environ.get('STATIC_DIR', 'static')
    rpi_relay.init_RPi()
    scheduler = BackgroundScheduler()
    scheduler.start()

    scheduler.add_job(_event_handler, 'interval', seconds=conf.EVENT_LOOP_INTERVAL)
    scheduler.add_job(_bangbang_controller, 'interval', seconds=conf.BANGBANG_LOOP_INTERVAL)
    logger.warn('starting scheduler')
    logger.warn('starting web server')
    app.run(debug=False, host='0.0.0.0')
