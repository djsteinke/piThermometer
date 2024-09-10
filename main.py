import requests
import logging

import datetime as dt
from datetime import timezone
from time import sleep

import firebase_db
import sensor

# create logger with 'spam_application'
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('/home/pi/projects/piThermometer/log.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


update_current_interval = 300   # 5 mins
add_history_interval = 1200  # 20 mins
get_current_interval = 60

last_update_current = dt.datetime.utcnow()
last_update_current = last_update_current.replace(tzinfo=timezone.utc)
last_add_history = dt.datetime.utcnow()
last_add_history = last_add_history.replace(tzinfo=timezone.utc)
last_get_current = dt.datetime.utcnow()
last_get_current = last_get_current.replace(tzinfo=timezone.utc)

current = {
    "dt": 0,
    "h": 0,
    "c": 0,
    "f": 0
}

history = {
    "dt": 1683561109,
    "h": 28.8,
    "t": 20.56
}

server_down = False


def add_history(now):
    global last_add_history
    try:
        c_dt = dt.datetime.utcfromtimestamp(current["dt"])
        c_dt = c_dt.replace(tzinfo=timezone.utc)
        # logger.debug(f"now: {now}, last_add_history: {last_add_history}")
        if last_add_history < now and c_dt > last_add_history:
            val = {"dt": round(now.timestamp()), "h": current["h"], "t": current["c"]}
            firebase_db.add_history(val)
            last_add_history += dt.timedelta(seconds=add_history_interval)
            logger.debug("add_history() complete")
    except Exception as e:
        logger.error("ERROR : add_history() : " + str(e))



def update_current(now):
    global last_update_current
    try:
        # logger.debug(f"now: {now}, last_add_history: {last_update_current}")
        c_dt = dt.datetime.utcfromtimestamp(current["dt"])
        c_dt = c_dt.replace(tzinfo=timezone.utc)
        if last_update_current < now and c_dt > last_update_current:
            dt_str = c_dt.isoformat()
            val = {"dt": dt_str.split("+")[0], "h": current["h"], "t": current["c"], "tF": current["f"]}
            firebase_db.update_current(val)
            last_update_current += dt.timedelta(seconds=update_current_interval)
    except Exception as e:
        logger.error("ERROR : update_current() : " + str(e))


def get_current(now):
    global current, last_get_current, server_down
    try:
        if last_get_current < now:
            old_dt = current['dt']
            current = sensor.check_sensor(now)
            if current['h'] > -1:
                current["dt"] = round(now.timestamp())
            else:
                current["dt"] = old_dt
            last_get_current = now + dt.timedelta(seconds=get_current_interval)
    except Exception as e:
        logger.error("ERROR : get_current() : " + str(e))


def main():
    while True:
        now = dt.datetime.utcnow()
        now = now.replace(tzinfo=timezone.utc)
        firebase_db.check_network(now)
        get_current(now)
        update_current(now)
        add_history(now)
        sleep(5)


if __name__ == '__main__':
    main()
