from http import HTTPStatus
from unittest.mock import patch, Mock

from pytest import fixture

from tests.unit.payloads_for_tests import (
    QRADAR_OBSERVE_RESPONSES_FOR_POST,
    QRADAR_OBSERVE_RESPONSES_FOR_GET
)
from .utils import headers


def routes():
    yield '/observe/observables'
    yield '/refer/observables'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


@fixture(scope='module')
def invalid_json():
    return [{'type': 'unknown', 'value': 'https://google.com'}]


@fixture(scope='module')
def valid_json():
    return [{"type": "ip", "value": "127.0.0.1"}]


@fixture(scope='module')
def valid_json_multiple():
    return [
        {"type": "ip", "value": "127.0.0.1"},
        {"type": "ip", "value": "1.2.3.4"}
    ]


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
@patch('jwt.PyJWKClient.fetch_data')
def test_enrich_call_success(
        fetch_data_mock, mocked_get, mocked_post, route,
        client, valid_jwt, valid_json,
        jwks_host_response, success_enrich_expected_body
):
    fetch_data_mock.return_value = jwks_host_response
    mocked_post.side_effect = build_side_effect('POST')
    mocked_get.side_effect = build_side_effect('GET')
    response = client.post(
        route, headers=headers(valid_jwt()), json=valid_json
    )

    json = response.get_json()
    if route == '/observe/observables':
        sightings = json['data']['sightings']
        assert sightings['count'] == 2
        for sighting in sightings['docs']:
            sighting.pop('id')

    assert response.status_code == HTTPStatus.OK
    assert json == success_enrich_expected_body


@patch('requests.post')
@patch('requests.get')
@patch('jwt.PyJWKClient.fetch_data')
def test_enrich_with_extended_error_handling(
        fetch_data_mock, mocked_get, mocked_post, route,
        client, valid_jwt, valid_json_multiple,
        jwks_host_response, success_enrich_expected_body,
        internal_errors_expected_payload, qradar_response_internal_error
):
    if route == '/observe/observables':
        fetch_data_mock.return_value = jwks_host_response
        mocked_post.side_effect = build_side_effect('POST')

        mocked_get.side_effect = [
            *build_side_effect('GET'), qradar_response_internal_error
        ]
        response = client.post(
            route, headers=headers(valid_jwt()), json=valid_json_multiple
        )

        json = response.get_json()
        if route == '/observe/observables':
            sightings = json['data']['sightings']
            assert sightings['count'] == 2
            for sighting in sightings['docs']:
                sighting.pop('id')

        assert response.status_code == HTTPStatus.OK
        assert json['data'] == success_enrich_expected_body['data']
        assert json['errors'] == internal_errors_expected_payload['errors']


def test_enrich_call_with_invalid_json_success(
        route, client, valid_jwt, invalid_json,
        invalid_json_expected_body):
    response = client.post(route,
                           headers=headers(valid_jwt()),
                           json=invalid_json)
    assert response.get_json() == invalid_json_expected_body


@patch('requests.post')
@patch('jwt.PyJWKClient.fetch_data')
def test_enrich_call_500(
        fetch_data_mock, mocked_post, route, client, valid_jwt,
        valid_json, jwks_host_response, internal_errors_expected_payload,
        qradar_response_internal_error
):
    if route == 'observe/observables':
        fetch_data_mock.return_value = jwks_host_response
        mocked_post.return_value = qradar_response_internal_error

        response = client.post(
            route, headers=headers(valid_jwt()), json=valid_json
        )
        assert response.status_code == HTTPStatus.OK
        assert response.get_json() == internal_errors_expected_payload
