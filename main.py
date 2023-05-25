import requests
import logging

import datetime as dt

import firebase_db


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
last_add_history = dt.datetime.utcnow()
last_get_current = dt.datetime.utcnow()

current = {
    "dt": 0,
    "h": 0,
    "t": 0,
    "tF": 0
}

history = {
    "dt": 1683561109,
    "h": 28.8,
    "t": 20.56
}


def add_history(now):
    global last_add_history
    c_dt = dt.datetime.utcfromtimestamp(current["dt"])
    if last_add_history < now and c_dt > last_add_history:
        val = {"dt": now.timestamp(), "h": current["h"], "t": current["t"], "tF": current["tF"]}
        firebase_db.add_history(val)
        last_add_history += dt.timedelta(seconds=add_history_interval)


def update_current(now):
    global last_update_current
    if last_update_current < now:
        c_dt = dt.datetime.utcfromtimestamp(current["dt"])
        val = {"dt": c_dt.isoformat(), "h": current["h"], "t": current["t"], "tF": current["tF"]}
        firebase_db.update_current(val)
        last_update_current += dt.timedelta(seconds=update_current_interval)


def get_current(now):
    global current, last_get_current
    if last_get_current < now:
        x = requests.get("http://192.168.0.160")
        if x.status_code == 200:
            current = x.json()
        else:
            logger.error("get_current() : " + str(x.status_code))
        last_get_current = now + dt.timedelta(seconds=get_current_interval)


def main():
    while True:
        now = dt.datetime.utcnow()
        firebase_db.check_network(now)
        get_current(now)
        update_current(now)
        add_history(now)


if __name__ == '__main__':
    main()
