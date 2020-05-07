from flask import Blueprint, current_app
from .ariel_search_client import ArialSearchClient

from api.utils import get_credentials, jsonify_data


health_api = Blueprint('health', __name__)


@health_api.route('/health', methods=['POST'])
def health():
    api_client = ArialSearchClient(get_credentials(), current_app.config)

    api_client.get_searches(range_start=0, range_end=5)

    return jsonify_data({'status': 'ok'})
