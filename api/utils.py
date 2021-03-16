from datetime import datetime
from urllib.error import URLError

import jwt
from flask import request, current_app, jsonify
from jwt import (
    PyJWKClient, InvalidSignatureError, InvalidAudienceError,
    DecodeError, PyJWKClientError
)
from requests.exceptions import ConnectionError

from api.errors import (
    BadRequestError,
    AuthorizationError,
    QRadarConnectionError
)

NO_AUTH_HEADER = 'Authorization header is missing'
WRONG_AUTH_TYPE = 'Wrong authorization type'
WRONG_PAYLOAD_STRUCTURE = 'Wrong JWT payload structure'
WRONG_JWT_STRUCTURE = 'Wrong JWT structure'
WRONG_AUDIENCE = 'Wrong configuration-token-audience'
KID_NOT_FOUND = 'kid from JWT header not found in API response'
WRONG_KEY = ('Failed to decode JWT with provided key. '
             'Make sure domain in custom_jwks_host '
             'corresponds to your SecureX instance region.')
JWKS_HOST_MISSING = ('jwks_host is missing in JWT payload. Make sure '
                     'custom_jwks_host field is present in module_type')
WRONG_JWKS_HOST = ('Wrong jwks_host in JWT payload. Make sure domain follows '
                   'the visibility.<region>.cisco.com structure')


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
    expected_errors = {
        KeyError: WRONG_PAYLOAD_STRUCTURE,
        AssertionError: JWKS_HOST_MISSING,
        InvalidSignatureError: WRONG_KEY,
        DecodeError: WRONG_JWT_STRUCTURE,
        InvalidAudienceError: WRONG_AUDIENCE,
        PyJWKClientError: KID_NOT_FOUND,
        URLError: WRONG_JWKS_HOST
    }

    try:
        token = get_auth_token()
        jwks_host = jwt.decode(
            token, options={'verify_signature': False}
        ).get('jwks_host')
        assert jwks_host

        jwks_client = PyJWKClient(f'https://{jwks_host}/.well-known/jwks')
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        aud = request.url_root
        payload = jwt.decode(
            token, signing_key.key,
            algorithms=['RS256'], audience=[aud.rstrip('/')]
        )
        current_app.config['SERVER_IP'] = payload['SERVER_IP']

        return payload['user'], payload['pass']
    except tuple(expected_errors) as error:
        raise AuthorizationError(expected_errors[error.__class__])


def get_auth_token():
    """
    Parse the incoming request's Authorization header and validate it.
    """

    expected_errors = {
        KeyError: NO_AUTH_HEADER,
        AssertionError: WRONG_AUTH_TYPE
    }
    try:
        scheme, token = request.headers['Authorization'].split()
        assert scheme.lower() == 'bearer'
        return token
    except tuple(expected_errors) as error:
        raise AuthorizationError(expected_errors[error.__class__])


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
