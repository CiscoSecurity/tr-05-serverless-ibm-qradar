import os
from datetime import timedelta

from version import VERSION


class Config:
    VERSION = VERSION

    SECRET_KEY = os.environ.get('SECRET_KEY', '')
    SERVER_IP = os.environ.get('SERVER_IP', '192.168.240.149')

    ARIAL_VERSION = '12.0'

    TOTAL_TIME_INTERVAL = timedelta(minutes=10)
    TIME_DELTA = timedelta(minutes=5)

    HEADERS = {
        'Accept': 'application/json',
        'Version': '12.0',
    }
    BASE_URI = '/api/'
