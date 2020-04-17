from authlib.jose import jwt
from authlib.jose.errors import JoseError
from flask import request, current_app, jsonify
from api.errors import (
    BadRequestError,
    QRadarInvalidCredentialsError,
)


def url_for(endpoint):
    return current_app.config['QRADAR_API_URL'].format(
        endpoint=endpoint,
    )


def get_credentials():
    try:
        scheme, token = request.headers['Authorization'].split()
        assert scheme.lower() == 'bearer'
        payload = jwt.decode(token, current_app.config['SECRET_KEY'])
        return payload.get('credentials')
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
