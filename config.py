__author__ = 'Conor'

# Enums -> http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python

from enum import Enum


class Config(Enum):
    PUB_TOPIC = 0
    SUB_TOPIC = 1
    ADDRESSES = 2
    PUB_ADDRESS = 3
    PUB_INTERVAL = 4
    TIME_OUT = 5
    SERVICES = 6
    WEB_SERVICE_URL = 7
    FIREBASE_URL = 8