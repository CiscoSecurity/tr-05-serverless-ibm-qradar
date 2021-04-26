from uuid import uuid4

import arrow
from flask import current_app


class Mapping:
    @staticmethod
    def extract_time(timestamp):
        return arrow.get(timestamp).datetime

    def observed_time(self, event):
        start_time = self.extract_time(event['starttime'])
        if event.get('endtime'):
            end_time = self.extract_time(event['endtime'])
        else:
            end_time = start_time
        return {
            'start_time': start_time.isoformat().replace("+00:00", "Z"),
            'end_time': end_time.isoformat().replace("+00:00", "Z")
        }

    @staticmethod
    def get_relations(event):
        if ((event.get("sourceip") and event.get("destinationip")) and
                (event["sourceip"] != event["destinationip"])):
            return [
                {
                    "related": {
                        "type": "ip",
                        "value": event['destinationip']
                    },
                    "source": {
                        "type": "ip",
                        "value": event["sourceip"]
                    },
                    **current_app.config['RELATIONS_DEFAULTS']
                }
            ]
        else:
            return []

    def targets(self, event):
        observables = []

        if event.get('sourceip'):
            observables.append({'type': 'ip',
                                'value': event['sourceip']})
        if event.get('sourcev6'):
            observables.append({'type': 'ipv6',
                                'value': event['sourcev6']})
        if event.get('sourcemac'):
            observables.append({'type': 'mac_address',
                                'value': event['sourcemac']})
        if event.get('username'):
            observables.append({'type': 'user',
                                'value': event['username']})
        if not observables:
            return []

        target = {
            'observables': observables,
            'observed_time': self.observed_time(event),
            'type': 'endpoint',
        }

        return [target]

    def sighting(self, observable, event):
        return {
            'id': f'transient:sighting-{uuid4()}',
            'targets': self.targets(event),
            'relations': self.get_relations(event),
            'observables': [
                {
                    'type': 'ip',
                    'value': observable
                }
            ],
            'observed_time': self.observed_time(event),
            'short_description': f"Event '{event['event_name']}': "
                                 + event['event_descr'],
            'description': 'A QRadar SIEM record retrieved from log source '
                           f'**{event["logsource_name"]}** related to '
                           f'**"{observable}"**',
            **current_app.config['SIGHTING_DEFAULTS']
        }
