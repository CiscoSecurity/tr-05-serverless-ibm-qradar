from datetime import datetime
from urllib.error import URLError, HTTPError

import jwt
from flask import request, current_app, jsonify, g
from jwt import (
    PyJWKClient, InvalidSignatureError, InvalidAudienceError,
    DecodeError, PyJWKClientError, MissingRequiredClaimError
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


def set_ctr_entities_limit(payload):
    try:
        ctr_entities_limit = int(payload['CTR_ENTITIES_LIMIT'])
        assert ctr_entities_limit > 0
    except (KeyError, ValueError, AssertionError):
        ctr_entities_limit = current_app.config['CTR_DEFAULT_ENTITIES_LIMIT']
    current_app.config['CTR_ENTITIES_LIMIT'] = ctr_entities_limit


def get_time_intervals():
    end_time = datetime.now()
    start_time = end_time - current_app.config['TOTAL_TIME_INTERVAL']
    return start_time, end_time


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
        MissingRequiredClaimError: WRONG_PAYLOAD_STRUCTURE,
        InvalidAudienceError: WRONG_AUDIENCE,
        PyJWKClientError: KID_NOT_FOUND,
        URLError: WRONG_JWKS_HOST,
        HTTPError: WRONG_JWKS_HOST
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

        set_ctr_entities_limit(payload)
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


def format_docs(docs):
    return {'count': len(docs), 'docs': docs}


def jsonify_result():
    result = {'data': {}}

    if g.get('status'):
        result['data']['status'] = g.status

    if g.get('sightings'):
        result['data']['sightings'] = format_docs(g.sightings)

    if g.get('errors'):
        result['errors'] = g.errors
        if not result['data']:
            del result['data']

    return jsonify(result)


def join_url(parts):
    return '/'.join(parts)


def add_status(status):
    g.status = status


def filter_observables(relay_input):
    observables = []
    for observable in relay_input:
        type_ = observable['type'].lower()
        value = observable['value']
        if (type_ in current_app.config['QRADAR_OBSERVABLE_TYPES']
                and value not in observables):
            observables.append(value)

    return observables


def handle_auth_errors(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except UnicodeEncodeError:
            raise AuthorizationError()

    return wrapper
