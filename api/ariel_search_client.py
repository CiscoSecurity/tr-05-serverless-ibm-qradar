from .rest_api_client import RestApiClient


class ArialSearchClient(RestApiClient):

    def __init__(self, creds, config):

        self.base_url = 'ariel/searches'
        super(ArialSearchClient, self).__init__(
            credentials=creds, config=config
        )

    def get_searches(self, range_start=None, range_end=None):
        headers = {**self.headers}

        if range_start and range_end:
            headers['Range'] = f'items={range_start}-{range_end}'

        return self._get(self.base_url, headers)

    def create_search(self, query_expression):

        data = {'query_expression': query_expression}
        response = self._post(self.base_url, data=data)

        return response.get("search_id")

    def get_search_results(self, search_id, range_start=None, range_end=None):
        headers = {**self.headers}

        if range_start and range_end:
            headers['Range'] = f'items={range_start}-{range_end}'

        url = self._url_for(search_id, 'results')

        return self._get(url, headers)

    def get_metadata(self, search_id, params):
        url = self._url_for(search_id, 'metadata')

        response = self._get(url, self.headers, params)
        return response.get("columns")

    def _url_for(self, search_id, endpoint):
        return '/'.join([self.base_url, search_id, endpoint])
