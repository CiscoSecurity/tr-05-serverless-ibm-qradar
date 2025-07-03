from .utils import headers
from pytest import fixture
from http import HTTPStatus
from unittest.mock import patch, MagicMock
from urllib.error import URLError
from api.utils import (
    NO_AUTH_HEADER,
    WRONG_AUTH_TYPE,
    WRONG_JWT_STRUCTURE,
    WRONG_PAYLOAD_STRUCTURE,
    WRONG_JWKS_HOST,
    KID_NOT_FOUND,
    WRONG_AUDIENCE,
    WRONG_KEY, JWKS_HOST_MISSING
)


def routes():
    yield '/health'
    yield '/refer/observables'
    yield '/observe/observables'
    yield '/respond/observables'
    yield '/respond/trigger'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


@fixture(scope='module')
def valid_json(route):
    if route.endswith('/trigger'):
        return {'observable_type': 'ip',
                'observable_value': '1.1.1.1',
                'reference_set_name': 'Database Servers',
                'action-id': 'qradar-add-to-reference-set'}
    return [{'type': 'ip', 'value': '1.1.1.1'}]


def test_call_with_authorization_header_missing(
        route, client, valid_json, authorization_errors_expected_payload
):
    response = client.post(route, json=valid_json)

    assert response.status_code == HTTPStatus.OK
    assert response.json == authorization_errors_expected_payload(
        NO_AUTH_HEADER
    )


def test_call_with_authorization_type_error(
        route, client, valid_json, authorization_errors_expected_payload):
    response = client.post(
        route, json=valid_json, headers={'Authorization': 'Basic blabla'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == authorization_errors_expected_payload(
        WRONG_AUTH_TYPE
    )


def test_call_with_jwt_structure_error(route, client, valid_json,
                                       authorization_errors_expected_payload):
    response = client.post(
        route, json=valid_json, headers={'Authorization': 'Bearer blabla'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == authorization_errors_expected_payload(
        WRONG_JWT_STRUCTURE
    )


@patch('jwt.PyJWKClient.fetch_data')
def test_call_with_missing_jwks_host(
        mock_request, route, client, valid_json, valid_jwt,
        authorization_errors_expected_payload, jwks_host_response
):
    mock_request.side_effect = jwks_host_response

    response = client.post(
        route, json=valid_json,
        headers=headers(valid_jwt(jwks_host=''))
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json == authorization_errors_expected_payload(
        JWKS_HOST_MISSING
    )


@patch('jwt.PyJWKClient.fetch_data')
def test_call_with_wrong_key(
        mock_request, route, client, valid_json, valid_jwt,
        authorization_errors_expected_payload, wrong_jwks_host_response
):
    mock_request.return_value = wrong_jwks_host_response

    response = client.post(
        route, json=valid_json,
        headers=headers(valid_jwt())
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json == authorization_errors_expected_payload(
        WRONG_KEY
    )


@patch('jwt.PyJWKClient.fetch_data')
def test_call_with_jwt_payload_structure_error(
        mock_request, route, client, valid_json, valid_jwt,
        jwks_host_response,
        authorization_errors_expected_payload
):
    mock_request.return_value = jwks_host_response
    response = client.post(
        route, json=valid_json,
        headers=headers(valid_jwt(wrong_structure=True))
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == authorization_errors_expected_payload(
        WRONG_PAYLOAD_STRUCTURE
    )


@patch('jwt.PyJWKClient.fetch_data')
@patch('requests.post')
def test_call_auth_failure_on_qradar_side(
        post_request, fetch_data_mock, route, client,
        valid_json, valid_jwt, authorization_errors_expected_payload,
        jwks_host_response, qradar_api_request,
        qradar_response_unauthorized_creds
):
    if route != '/refer/observables':
        fetch_data_mock.return_value = jwks_host_response
        qradar_api_request.return_value = qradar_response_unauthorized_creds
        post_request.return_value = qradar_response_unauthorized_creds

        response = client.post(
            route, json=valid_json,
            headers=headers(valid_jwt())
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json == authorization_errors_expected_payload(
            'Authorization failed on QRadar side'
        )


@patch('jwt.PyJWKClient.fetch_data')
def test_call_with_wrong_audience(
        fetch_data_mock, route, client, valid_json, valid_jwt,
        authorization_errors_expected_payload,
        jwks_host_response
):
    fetch_data_mock.return_value = jwks_host_response

    response = client.post(
        route, json=valid_json,
        headers=headers(valid_jwt(aud='wrong_aud'))
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json == authorization_errors_expected_payload(
        WRONG_AUDIENCE
    )


@patch('jwt.PyJWKClient.fetch_data')
def test_call_with_wrong_kid(
        fetch_data_mock, route, client, valid_json, valid_jwt,
        authorization_errors_expected_payload,
        jwks_host_response
):
    fetch_data_mock.return_value = jwks_host_response

    response = client.post(
        route, json=valid_json,
        headers=headers(valid_jwt(kid='wrong_kid'))
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json == authorization_errors_expected_payload(
        KID_NOT_FOUND
    )


@patch('jwt.PyJWKClient.fetch_data')
def test_call_with_wrong_jwks_host(
        fetch_data_mock, route, client, valid_json, valid_jwt,
        authorization_errors_expected_payload
):
    mock_exception = MagicMock()
    mock_exception.reason = 'test'
    fetch_data_mock.side_effect = URLError(mock_exception)

    response = client.post(
        route, json=valid_json, headers=headers(valid_jwt())
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == authorization_errors_expected_payload(
        WRONG_JWKS_HOST
    )
