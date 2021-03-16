from functools import partial
from .ariel_search_client import ArialSearchClient
from .arial_query import ArialQuery

from flask import Blueprint, current_app

from api.schemas import ObservableSchema
from api.utils import (get_json, get_credentials,
                       jsonify_data, get_time_intervals)


enrich_api = Blueprint('enrich', __name__)

get_observables = partial(get_json, schema=ObservableSchema(many=True))


@enrich_api.route('/deliberate/observables', methods=['POST'])
def deliberate_observables():
    # Not implemented
    return jsonify_data({})


@enrich_api.route('/observe/observables', methods=['POST'])
def observe_observables():
    api_client = ArialSearchClient(get_credentials(), current_app.config)
    arial_query = ArialQuery()
    observables = get_observables()
    query_with_limit = arial_query.build(limit=1)
    search_id = api_client.create_search(query_with_limit)

    params = {
        'fields': 'columns (name)',
        'filter': 'object_value_type in ("String","Host")'
    }
    names = api_client.get_metadata(search_id, params)

    relay_response = []

    times = get_time_intervals()
    searches = []
    for i in range(len(times) - 1):
        query_with_observables = arial_query.build(
            observables=observables,
            names=names,
            time=(times[i], times[i + 1])
        )
        if not query_with_observables:
            continue
        search_id = api_client.create_search(query_with_observables)
        searches.append(search_id)

    for search_id in searches:
        relay_response += \
            api_client.get_search_results(search_id)['events']
    return jsonify_data(relay_response)


def get_search_pivots(value):
    return {
        'id': f'ref-qradar-search-ip-{value}',
        'title': 'Search for this IP',
        'description': 'Lookup this IP on QRadar SIEM Event Viewer',
        'url': current_app.config['REFER_URL'].format(
            server_ip=current_app.config['SERVER_IP'],
            observable=value
        ),
        'categories': ['Search', 'QRadar SIEM']
    }


@enrich_api.route('/refer/observables', methods=['POST'])
def refer_observables():
    _ = get_credentials()
    observables = get_observables()
    if not observables:
        return jsonify_data([])

    relay_output = []

    for observable in observables:
        if observable['type'] == 'ip':
            relay_output.append(get_search_pivots(observable['value']))

    return jsonify_data(relay_output)
