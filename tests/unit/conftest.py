from http import HTTPStatus

import jwt
from pytest import fixture
from unittest.mock import MagicMock, patch

from api.errors import AUTH_ERROR
from app import app


@fixture(scope='session')
def client():
    app.rsa_private_key = '''-----BEGIN PRIVATE KEY-----
MIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEAmRkQUiQ271QKj2/L
eBefn4PIfHGLWyHGO8x76e29z4OzY7JLb6++924yT+IGOcevE3xFudFWL0LdXdAx
8X+lxQIDAQABAkAgbwriHAH3WdqS4KA+ZOLQLF8A3h0jxVf1uzBVMqSPnYbeWI1r
9uP/JTNi/aA1OLXjkc9NwlSyUMfev9eDSQHRAiEA2Kf9PZCeBw8AotXkQqYxdE9/
sWwjbjCatZXe4QINLG8CIQC05lkDdmgVwllOIIJQiqVKsPazI/pq5WfgGdCZ98WT
CwIhAMriTUAovANKJkNWXwGW1frgM2i3Jlqag1YGOYelvyZbAiA4zmz9bV1aF+G7
avIBIMivH8sYjh/BGbD46qJa9zeP6QIgGlUK1ITGubEVQgatyYW83bIBo3KKgglB
2KjYzPm0Bnk=
-----END PRIVATE KEY-----'''

    with app.test_client() as client:
        yield client


@fixture(scope='session')
def valid_jwt(client):
    def _make_jwt(
            jwks_host='visibility.amp.cisco.com',
            aud='http://localhost',
            kid='02B1174234C29F8EFB69911438F597FF3FFEE6B7',
            wrong_structure=False
    ):
        payload = {
            'user': 'arozl',
            'pass': 'mypass',
            'SERVER_IP': '1.2.3.4',
            'jwks_host': jwks_host,
            'aud': aud,
        }

        if wrong_structure:
            payload.pop('user')

        return jwt.encode(
            payload, client.application.rsa_private_key, algorithm='RS256',
            headers={
                'kid': kid
            }
        )

    return _make_jwt


@fixture(scope='session')
def jwks_host_response(client):
    return {'keys': [
        {
            'kty': 'RSA',
            'n': 'mRkQUiQ271QKj2_LeBefn4PIfHGLWyHGO8x76e'
                 '29z4OzY7JLb6--924yT-IGOcevE3xFudFWL0LdXdAx8X-lxQ',
            'e': 'AQAB',
            'alg': 'RS256',
            'kid': '02B1174234C29F8EFB69911438F597FF3FFEE6B7',
            'use': 'sig'
        }
    ]
    }


@fixture(scope='session')
def wrong_jwks_host_response(client):
    return {'keys': [
        {
            'kty': 'RSA',
            'n': 'jwVpCJSiQNvD9izsvPii12GcvmvXT5C6Jon'
                 'CmpuSpIP85pU2ssJua4tdM1mcR4BMGEHSEdIO25jH3dqUeK7VEw',
            'e': 'AQAB',
            'alg': 'RS256',
            'kid': '02B1174234C29F8EFB69911438F597FF3FFEE6B7',
            'use': 'sig'
        }
    ]
    }


@fixture(scope='module')
def authorization_errors_expected_payload(route):
    def _make_payload_message(message):
        payload = {
            'errors':
                [
                    {
                        'code': AUTH_ERROR,
                        'message': f'Authorization failed: {message}',
                        'type': 'fatal'
                    }
                ]

        }
        return payload

    return _make_payload_message


def qradar_api_response_mock(status_code, payload=None):
    mock_response = MagicMock()

    mock_response.status_code = status_code
    mock_response.ok = status_code == HTTPStatus.OK

    payload = payload or {}
    mock_response.json = lambda: payload

    return mock_response


@fixture(scope='module')
def qradar_response_unauthorized_creds():
    return qradar_api_response_mock(
        status_code=HTTPStatus.UNAUTHORIZED,
        payload={
            'message': 'You are unauthorized to access the requested resource.'
        }
    )


@fixture(scope='module')
def qradar_api_request():
    with patch('requests.get') as mock_request:
        yield mock_request


@fixture(scope='module')
def success_enrich_expected_body(
        route, success_refer_body, success_observe_body
):
    if route == '/observe/observables':
        return success_observe_body
    return success_refer_body


@fixture(scope='module')
def success_refer_body():
    return {
        'data': [
            {
                "id": "ref-qradar-search-ip-127.0.0.1",
                "title": "Search for this IP",
                "description": "Lookup this IP on QRadar SIEM Event Viewer",
                "categories": [
                    "Search",
                    "QRadar SIEM"
                ],
                "url": "https://1.2.3.4/console/do/ariel/arielSearch?"
                       "appName=EventViewer&pageId=EventList&dispatch="
                       "performSearch&value(timeRangeType)=aqlTime&value"
                       "(searchMode)=AQL&value(aql)=SELECT * FROM events "
                       "WHERE sourceip='127.0.0.1' OR destinationip='"
                       "127.0.0.1' LAST 7 DAYS"
            }
        ]
    }


@fixture(scope='module')
def success_observe_body():
    return {
        "data": [
            {
                "utf8_payload": "May  8 07:47:00 127.0.0.1 [Thread-64]"
            },
            {
                "utf8_payload": "May  8 07:47:00 127.0.0.1 [Thread-64]"
            }
        ]
    }
