from http import HTTPStatus

from pytest import fixture
from unittest import mock
from unittest.mock import patch

from .utils import headers
from tests.unit.payloads_for_tests import (
    EXPECTED_PAYLOAD_500_ERROR,
    QRADAR_HEALTH_RESPONSE,
    QRADAR_500_ERROR_RESPONSE,
)


def routes():
    yield '/health'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


def qradar_api_response(*, ok):
    mock_response = mock.MagicMock()

    mock_response.ok = ok

    if ok:
        payload = QRADAR_HEALTH_RESPONSE

    else:
        payload = QRADAR_500_ERROR_RESPONSE
        mock_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    mock_response.json = lambda: payload

    return mock_response


@patch('jwt.PyJWKClient.fetch_data')
def test_health_call_success(
        fetch_data_mock, route, client, qradar_api_request,
        valid_jwt, jwks_host_response
):
    fetch_data_mock.return_value = jwks_host_response
    qradar_api_request.return_value = \
        qradar_api_response(ok=True)
    response = client.post(route, headers=headers(valid_jwt()))
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == {'data': {'status': 'ok'}}


@patch('jwt.PyJWKClient.fetch_data')
def test_health_call_500(
        fetch_data_mock, route, client, qradar_api_request,
        valid_jwt, jwks_host_response
):
    fetch_data_mock.return_value = jwks_host_response
    qradar_api_request.return_value = \
        qradar_api_response(ok=False)
    response = client.post(route, headers=headers(valid_jwt()))
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_PAYLOAD_500_ERROR
