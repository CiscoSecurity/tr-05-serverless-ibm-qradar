from functools import partial
from time import time
from .ariel_search_client import ArielSearchClient
from .ariel_query import ArielQuery
from .mapping import Mapping


from flask import Blueprint, current_app, g

from api.schemas import ObservableSchema
from api.utils import (get_json, get_credentials,
                       jsonify_data, jsonify_result,
                       get_time_intervals, filter_observables)
from api.errors import QRadarTimeoutError


enrich_api = Blueprint('enrich', __name__)

get_observables = partial(get_json, schema=ObservableSchema(many=True))


@enrich_api.route('/observe/observables', methods=['POST'])
def observe_observables():
    def query_qradar(obs):
        query_with_observables = arial_query.build(
            observable=obs,
            names=names,
            time=get_time_intervals(),
            limit=current_app.config['CTR_ENTITIES_LIMIT']
        )
        if not query_with_observables:
            return jsonify_data({})

        search_id, status = api_client.create_search(query_with_observables)

        start_time = time()
        while status != 'COMPLETED':
            if (time() - start_time
                    < current_app.config['SEARCH_TIMOUT_IN_SEC']):
                status = api_client.get_search(search_id)['status']
            else:
                raise QRadarTimeoutError

        return api_client.get_search_results(search_id)['events']

    relay_input = get_observables()
    observables = filter_observables(relay_input)

    if not observables:
        return jsonify_data({})

    api_client = ArielSearchClient(get_credentials(), current_app.config)
    arial_query = ArielQuery()

    params = {
        'fields': 'columns (name)',
        'filter': 'object_value_type = "Host"'
    }
    names = api_client.get_metadata(params)

    g.sightings = []
    for observable in observables:
        response = query_qradar(observable)
        for event in response:
            mapping = Mapping()
            g.sightings.append(mapping.sighting(observable, event))

    return jsonify_result()


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
    relay_input = get_observables()
    observables = filter_observables(relay_input)

    if not observables:
        return jsonify_data([])

    _ = get_credentials()

    relay_output = []

    for observable in observables:
        relay_output.append(get_search_pivots(observable))

    return jsonify_data(relay_output)
