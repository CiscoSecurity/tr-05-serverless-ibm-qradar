from .rest_api_client import RestApiClient
from .utils import join_url


class ReferenceDataClient(RestApiClient):

    def __init__(self, creds, config):

        self.base_url = 'reference_data/sets'
        self.set_source_default = config['REFERENCE_SET_DEFAULTS']
        self.set_element_type = config['REFERENCE_SET_ELEM_TYPE']
        super(ReferenceDataClient, self).__init__(
            credentials=creds, config=config
        )

    def get_reference_sets(self, params):
        response = self._get(self.base_url, self.headers, params)
        return response

    def get_reference_set_data(self, name):
        url = join_url([self.base_url, name])
        params = {'fields': 'data(value)'}
        response = self._get(url, self.headers, params)
        return response

    def add_to_reference_set(self, name, observable_value):
        url = join_url([self.base_url, name])
        return self._post(url, data={
            'value': observable_value, **self.set_source_default
        })

    def remove_from_reference_set(self, name, observable_value):
        url = join_url([self.base_url, name, observable_value])
        return self._delete(url, self.headers)

    def add_and_create_reference_set(self, name, observable_value):
        self._post(self.base_url, data={**self.set_element_type, 'name': name})
        return self.add_to_reference_set(name, observable_value)
