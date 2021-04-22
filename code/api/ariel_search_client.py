from .rest_api_client import RestApiClient


class ArielSearchClient(RestApiClient):

    def __init__(self, creds, config):

        self.base_url = 'ariel'
        super(ArielSearchClient, self).__init__(
            credentials=creds, config=config
        )

    def get_searches(self, range_start=None, range_end=None):
        headers = {**self.headers}

        if range_start and range_end:
            headers['Range'] = f'items={range_start}-{range_end}'

        return self._get(self._get_url(), headers)

    def create_search(self, query_expression):

        data = {'query_expression': query_expression}
        url = self._get_url()
        response = self._post(url, data=data)

        return response["search_id"], response["status"]

    def get_search_results(self, search_id, range_start=None, range_end=None):
        headers = {**self.headers}

        if range_start and range_end:
            headers['Range'] = f'items={range_start}-{range_end}'

        url = self._get_url(search_id, 'results')

        return self._get(url, headers)

    def get_metadata(self, params):
        url = self._get_url('events', query_endpoint='databases')

        response = self._get(url, self.headers, params)
        return response.get('columns')

    def get_search(self, search_id):
        url = self._get_url(search_id)
        return self._get(url, self.headers)

    def _get_url(self, *parts, query_endpoint='searches'):
        url = [self.base_url, query_endpoint, *parts]
        return '/'.join(url)
