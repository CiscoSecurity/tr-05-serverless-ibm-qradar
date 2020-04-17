from http import HTTPStatus

from pytest import fixture
from unittest import mock

from .utils import headers
from tests.unit.payloads_for_tests import (
    EXPECTED_PAYLOAD_PERMISSION_DENIED,
    EXPECTED_PAYLOAD_500_ERROR,
    QRADAR_HEALTH_RESPONSE,
    QRADAR_500_ERROR_RESPONSE,
)


def routes():
    yield '/health'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


@fixture(scope='function')
def qradar_api_request():
    with mock.patch('requests.get') as mock_request:
        yield mock_request


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


def test_health_call_success(route, client, qradar_api_request, valid_jwt):
    qradar_api_request.return_value = \
        qradar_api_response(ok=True)
    response = client.post(route, headers=headers(valid_jwt))
    assert response.status_code == HTTPStatus.OK


def test_health_call_with_invalid_jwt_failure(route, client, invalid_jwt):
    response = client.post(route, headers=headers(invalid_jwt))
    assert response.get_json() == EXPECTED_PAYLOAD_PERMISSION_DENIED


def test_health_call_500(route, client, qradar_api_request, valid_jwt):
    qradar_api_request.return_value = \
        qradar_api_response(ok=False)
    response = client.post(route, headers=headers(valid_jwt))
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_PAYLOAD_500_ERROR
