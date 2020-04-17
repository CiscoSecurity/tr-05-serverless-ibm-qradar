import os

from version import VERSION


class Config:
    VERSION = VERSION

    SECRET_KEY = os.environ.get('SECRET_KEY', '')

    QRADAR_API_URL = "https://192.168.240.149/api/ariel/{endpoint}"
