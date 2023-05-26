import firebase_admin
from firebase_admin import db
import logging
import requests
import datetime as dt
from datetime import timezone

module_logger = logging.getLogger('main.firebase_db')

databaseURL = "https://pitemperature-a22b2-default-rtdb.firebaseio.com"

cred_obj = firebase_admin.credentials.Certificate("/home/pi/projects/piTempFirebaseKey.json")
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': databaseURL
})

ref = db.reference("/")

current = ref.child('current')
history = ref.child('history')

histories = []
network_up = False
network_check_interval = 15
network_check_next = dt.datetime.utcnow()
network_check_next = network_check_next.replace(tzinfo=timezone.utc)


def update_error(val):
    if network_up:
        try:
            ref.child('error').set(val)
            module_logger.debug("update_error() :\n" + str(val))
        except Exception as e:
            module_logger.error("update_error() : " + str(e) + "\n" + str(val))


def update_current(val):
    if network_up:
        try:
            current.set(val)
            module_logger.debug("update_current() :\n" + str(val))
        except Exception as e:
            module_logger.error("update_current() : " + str(e) + "\n" + str(val))


def add_history(val):
    histories.append(val)
    module_logger.debug("add_history() :")
    while True:
        if network_up:
            try:
                h = histories[0]
                new_history = history.push()
                new_history.set(h)
                histories.pop(0)
                module_logger.debug("\n" + str(h))
                if len(histories) == 0:
                    break
            except Exception as e:
                module_logger.error("ERROR : " + str(e))
                break
        else:
            break


def check_network(now):
    global network_up, network_check_next
    if network_check_next < now:
        try:
            requests.get("https://google.com")
            if not network_up:
                module_logger.debug('network state : UP')
            network_up = True
            return network_up
        except:
            if network_up:
                module_logger.error('network state : DOWN')
            network_up = False
        network_check_next = now + dt.timedelta(seconds=network_check_interval)
