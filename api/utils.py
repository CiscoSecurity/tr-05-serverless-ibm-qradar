from authlib.jose import jwt
from authlib.jose.errors import JoseError
from requests.exceptions import ConnectionError
from datetime import datetime
from flask import request, current_app, jsonify
from api.errors import (
    BadRequestError,
    QRadarInvalidCredentialsError,
    QRadarConnectionError
)


def get_time_intervals():
    end_time = datetime.now()
    start_time = end_time - current_app.config['TOTAL_TIME_INTERVAL']
    delta = current_app.config['TIME_DELTA']
    times = []
    while start_time < end_time:
        times.append(start_time)
        start_time += delta
    times.append(end_time)
    return times


def handle_connection_error(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ConnectionError:
            raise QRadarConnectionError

    return wrapper


def get_credentials():
    try:
        scheme, token = request.headers['Authorization'].split()
        assert scheme.lower() == 'bearer'
        payload = jwt.decode(token, current_app.config['SECRET_KEY'])
        return payload.get('user'), payload.get('pass')
    except (KeyError, ValueError, AssertionError, JoseError):
        raise QRadarInvalidCredentialsError


def get_json(schema):
    data = request.get_json(force=True, silent=True, cache=False)

    message = schema.validate(data)

    if message:
        raise BadRequestError(message)

    return data


def jsonify_data(data):
    return jsonify({'data': data})


def jsonify_errors(error):
    return jsonify({'errors': [error]})
