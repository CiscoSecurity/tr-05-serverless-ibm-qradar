from collections import namedtuple
from http import HTTPStatus
from unittest.mock import patch

from pytest import fixture

from api.errors import INVALID_ARGUMENT
from api.respond import (
    ADD_ACTION_ID, REMOVE_ACTION_ID, ADD_AND_CRETE_ACTION_ID
)
from tests.unit.api.utils import headers


def routes():
    yield '/respond/observables'
    yield '/respond/trigger'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


@fixture(scope='module')
def invalid_json(route):
    if route.endswith('/observables'):
        return [{'type': 'ip'}]

    if route.endswith('/trigger'):
        return {'observable_type': 'ip',
                'observable_value': '1.1.1.1',
                'reference_set_name': 'Set'}


def test_respond_call_with_valid_jwt_but_invalid_json_failure(
        route, client, valid_jwt, invalid_json, invalid_json_expected_payload
):
    response = client.post(
        route, headers=headers(valid_jwt()), json=invalid_json
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == invalid_json_expected_payload


@patch('jwt.PyJWKClient.fetch_data')
@patch('requests.get')
def test_respond_observables_call_success(
        request_mock, fetch_data_mock, client, valid_jwt,
        qradar_response_reference_sets, respond_observables_expected_payload,
        jwks_host_response, qradar_response_set_data
):
    fetch_data_mock.return_value = jwks_host_response
    request_mock.side_effect = (
        qradar_response_reference_sets, qradar_response_set_data
    )

    response = client.post(
        '/respond/observables', headers=headers(valid_jwt()),
        json=[{'type': 'ip', 'value': '1.1.1.1'}]
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == respond_observables_expected_payload


def input_sets():
    input_json = {'observable_type': 'ip',
                  'observable_value': '1.1.1.1',
                  'reference_set_name': 'Database Servers'}
    expected_response_success = {'data': {'status': 'success'}}

    TestData = namedtuple(
        'TestData', 'test_name json expected_response method'
    )
    yield TestData(
        'add_action_success',
        {**input_json, 'action-id': ADD_ACTION_ID},
        expected_response_success,
        'post'
    )

    yield TestData(
        'add_and_create_action_success',
        {**input_json, 'action-id': ADD_AND_CRETE_ACTION_ID},
        expected_response_success,
        'post'
    )

    yield TestData(
        'remove_action_success',
        {**input_json, 'action-id': REMOVE_ACTION_ID},
        expected_response_success,
        'delete'
    )

    yield TestData(
        'unsupported_action_failure',
        {**input_json, 'action-id': 'unknown'},
        {
            'data': {'status': 'failure'},
            'errors': [
                {'code': INVALID_ARGUMENT,
                 'message': 'Unsupported action.',
                 'type': 'fatal'}
            ]
        },
        'post'
    )


@fixture(scope='module', params=input_sets(), ids=lambda data: data.test_name)
def input_data(request):
    return request.param


@patch('jwt.PyJWKClient.fetch_data')
def test_respond_trigger(
        fetch_data_mock, input_data, client, valid_jwt,
        post_reference_set_response, jwks_host_response
):
    with patch(f'requests.{input_data.method}') as request_mock:
        fetch_data_mock.return_value = jwks_host_response
        request_mock.return_value = post_reference_set_response

        response = client.post(
            '/respond/trigger', headers=headers(valid_jwt()),
            json=input_data.json
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json == input_data.expected_response
