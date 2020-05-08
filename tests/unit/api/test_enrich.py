from http import HTTPStatus

from pytest import fixture
from unittest.mock import patch, Mock

from .utils import headers
from tests.unit.payloads_for_tests import (
    EXPECTED_PAYLOAD_PERMISSION_DENIED,
    EXPECTED_PAYLOAD_SUCCESS,
    EXPECTED_PAYLOAD_500_ERROR,
    QRADAR_OBSERVE_RESPONSES_FOR_POST,
    QRADAR_OBSERVE_RESPONSES_FOR_GET,
    QRADAR_500_ERROR_RESPONSE,
)


def routes():
    yield '/observe/observables'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


@fixture(scope='module')
def invalid_json():
    return [{'type': 'unknown', 'value': 'https://google.com'}]


@fixture(scope='module')
def valid_json():
    return [{"type": "ip", "value": "127.0.0.1"}]


def build_side_effect(method):
    side_effects = []
    expected_payloads = []
    if method == 'POST':
        expected_payloads = QRADAR_OBSERVE_RESPONSES_FOR_POST
    if method == 'GET':
        expected_payloads = QRADAR_OBSERVE_RESPONSES_FOR_GET
    for payload in expected_payloads:
        side_effects.append(Mock(status_code=200, json=lambda: payload))
    return side_effects


@patch('requests.post')
@patch('requests.get')
def test_enrich_call_success(mocked_get, mocked_post, route,
                             client, valid_jwt, valid_json):
    mocked_post.side_effect = build_side_effect('POST')
    mocked_get.side_effect = build_side_effect('GET')
    response = client.post(route, headers=headers(valid_jwt), json=valid_json)
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_PAYLOAD_SUCCESS


def test_enrich_call_with_invalid_jwt_failure(route, client, invalid_jwt):
    response = client.post(route, headers=headers(invalid_jwt))
    assert response.get_json() == EXPECTED_PAYLOAD_PERMISSION_DENIED


@patch('requests.post')
def test_enrich_call_500(mocked_post, route, client, valid_jwt, valid_json):
    mocked_post.return_value = Mock(
        ok=False,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        json=lambda: QRADAR_500_ERROR_RESPONSE
    )
    response = client.post(route, headers=headers(valid_jwt), json=valid_json)
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_PAYLOAD_500_ERROR
