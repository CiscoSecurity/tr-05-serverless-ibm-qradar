class ArielQuery:
    def __init__(self):
        self.base_query = "SELECT * FROM events"

    def build(self, observable=None,
              names=None, time=None, limit=None):
        query = [self.base_query]
        if observable and names:
            clauses = self._get_clauses(observable, names)
            if not clauses:
                return ''
            query.append(clauses)
        if limit:
            query.append(self._get_limit(limit))
        if time:
            query.append(self._get_interval(*time))

        return ' '.join(query)

    @staticmethod
    def _get_limit(number):
        return f"LIMIT {number}"

    @staticmethod
    def _get_clauses(observable, names):
        condition = []

        fields = [d['name'] for d in names]
        for field in fields:
            if ' ' in field:
                condition.append(f"'{field}'='{observable}'")
            else:
                condition.append(f"{field}='{observable}'")

        if not condition:
            return ''
        query = f"WHERE {' OR '.join(condition)} "
        return query

    @staticmethod
    def _get_interval(start, stop):
        return f"START '{start}' STOP '{stop}'"
