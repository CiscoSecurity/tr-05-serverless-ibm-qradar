import requests
import urllib3
from base64 import b64encode
from flask import Blueprint

from api.utils import get_credentials, jsonify_data, url_for
from api.errors import (QRadarUnexpectedError,
                        QRadarConnectionError
                        )


health_api = Blueprint('health', __name__)


@health_api.route('/health', methods=['POST'])
def health():
    credentials = get_credentials()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Range': 'items=0-49',
        'Version': '12.0',
        'Authorization':
            f'Basic {b64encode(credentials.encode("utf-8")).decode("utf-8")}'
    }
    url = url_for('searches')

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        response = requests.get(url, headers=headers, verify=False)
    except requests.exceptions.ConnectionError:
        raise QRadarConnectionError

    if response.ok:
        return jsonify_data({'status': 'ok'})
    else:
        raise QRadarUnexpectedError(response)
