import requests
import urllib3
from http import HTTPStatus
from api.errors import (
    QRadarInternalServerError,
    QRadarUnexpectedError,
    AuthorizationError,
)
from .utils import handle_connection_error


class RestApiClient:

    def __init__(self, credentials=None, config=None):
        self.headers = config['HEADERS']
        self.credentials = credentials
        self.server_ip = config['SERVER_IP']
        self.base_uri = config['BASE_URI']

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @staticmethod
    def _get_response_data(response):
        if response.ok:
            return response.json()
        else:
            expected_response_errors = {
                HTTPStatus.UNAUTHORIZED: AuthorizationError,
                HTTPStatus.INTERNAL_SERVER_ERROR: QRadarInternalServerError,
            }

            if response.status_code in expected_response_errors:
                raise expected_response_errors[response.status_code]
            else:
                raise QRadarUnexpectedError(response)

    @handle_connection_error
    def _get(self, endpoint, headers=None, params=None):
        response = requests.get(
            f'https://{self.server_ip}{self.base_uri}{endpoint}',
            headers=headers, verify=False, auth=self.credentials,
            params=params)
        return self._get_response_data(response)

    @handle_connection_error
    def _post(self, endpoint, data=None):
        response = requests.post(
            f'https://{self.server_ip}{self.base_uri}{endpoint}',
            data, headers=self.headers, verify=False, auth=self.credentials)
        return self._get_response_data(response)

    @handle_connection_error
    def _delete(self, endpoint, headers):
        response = requests.delete(
            f'https://{self.server_ip}{self.base_uri}{endpoint}',
            headers=headers, verify=False, auth=self.credentials)
        return self._get_response_data(response)
