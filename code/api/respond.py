from flask import Blueprint, current_app

from api.errors import InvalidArgumentError
from api.reference_data_client import ReferenceDataClient
from api.utils import jsonify_data, get_credentials, add_status, jsonify_result
from functools import partial
from api.schemas import ObservableSchema, ActionFormParamsSchema
from api.utils import get_json, filter_observables

get_observables = partial(get_json, schema=ObservableSchema(many=True))
get_action_form_params = partial(get_json, schema=ActionFormParamsSchema())

respond_api = Blueprint('respond', __name__)

ADD_ACTION_ID = 'qradar-add-to-reference-set'
REMOVE_ACTION_ID = 'qradar-remove-from-reference-set'
ADD_AND_CRETE_ACTION_ID = 'qradar-add-and-create-reference-set'


def add_to(observable, name):
    return action(
        ADD_ACTION_ID,
        'Add to {} Reference Set',
        'Add {} to Reference Set',
        observable,
        name
    )


def remove_from(observable, name):
    return action(
        REMOVE_ACTION_ID,
        'Remove from {} Reference Set',
        'Remove {} from Reference Set',
        observable,
        name
    )


def add_and_create(observable):
    return action(
        ADD_AND_CRETE_ACTION_ID,
        'Create a Reference Set and add an observable to it',
        'Add {} to SecureX Investigation Reference Set',
        observable,
        'SecureX Investigation'
    )


def action(
        id_, title_template, description_template, observable, name
):
    return {
        'id': id_,
        'title': title_template.format(name),
        'description':
            description_template.format(
                'IP'
            ),
        'categories': ['QRadar SIEM'],
        'query-params': {
            'observable_value': observable,
            'observable_type': 'ip',
            'reference_set_name': name
        }
    }


@respond_api.route('/respond/observables', methods=['POST'])
def respond_observables():
    relay_input = get_observables()
    observables = filter_observables(relay_input)

    api_client = ReferenceDataClient(get_credentials(), current_app.config)
    params = {
        'filter': 'element_type = "IP"',
        'fields': 'number_of_elements, name'
    }
    result = api_client.get_reference_sets(params)
    actions = []
    securex_set_absent = True
    for observable in observables:
        for set_ in result:
            if set_['name'] == current_app.config['SECUREX_SET_NAME']:
                securex_set_absent = False
            if set_['number_of_elements'] > 0:
                data = api_client.get_reference_set_data(set_['name'])
                if observable in str(data):
                    actions.append(remove_from(observable, set_['name']))
                    continue
            else:
                actions.append(add_to(observable, set_['name']))
        if securex_set_absent:
            actions.append(add_and_create(observable))
            securex_set_absent = True

    actions.sort(key=lambda item: item['title'])

    return jsonify_data(actions)


@respond_api.route('/respond/trigger', methods=['POST'])
def respond_trigger():
    add_status('failure')

    params = get_action_form_params()

    client = ReferenceDataClient(get_credentials(), current_app.config)
    action_map = {
        ADD_ACTION_ID: client.add_to_reference_set,
        REMOVE_ACTION_ID: client.remove_from_reference_set,
        ADD_AND_CRETE_ACTION_ID: client.add_and_create_reference_set
    }

    action = action_map.get(params['action-id'])
    if not action:
        raise InvalidArgumentError('Unsupported action.')

    action(params['reference_set_name'], params['observable_value'])

    add_status('success')
    return jsonify_result()
