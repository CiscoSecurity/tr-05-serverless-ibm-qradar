class ArialQuery:
    def __init__(self):
        self.base_query = "SELECT UTF8(payload) FROM events"

    def build(self, observables=None,
              names=None, time=None, limit=None):
        query = [self.base_query]
        if observables and names:
            clauses = self._get_clauses(observables, names)
            if not clauses:
                return ''
            query.append(clauses)
        if time:
            query.append(self._get_interval(*time))
        if limit:
            query.append(self._get_limit(limit))

        return ' '.join(query)

    @staticmethod
    def _get_limit(number):
        return f"LIMIT {number}"

    @staticmethod
    def _get_clauses(observables, names):
        condition = []
        for observable in observables:
            type = observable.get('type')
            fields = [d['name'] for d in names if type in d['name'].lower()]
            for field in fields:
                if field.count(' '):
                    condition.append(f"'{field}'='{observable.get('value')}'")
                else:
                    condition.append(f"{field}='{observable.get('value')}'")

        if not condition:
            return ''
        query = f"WHERE {' OR '.join(condition)} "
        return query

    @staticmethod
    def _get_interval(start, stop):
        return f"START '{start}' STOP '{stop}'"
