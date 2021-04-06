EXPECTED_PAYLOAD_500_ERROR = {
  "errors": [
    {
      "code": "internal error",
      "message": "The QRadar internal error.",
      "type": "fatal"
    }
  ]
}

EXPECTED_PAYLOAD_PERMISSION_DENIED = {
  "errors": [
    {
      "code": "permission denied",
      "message": "The request is missing valid credentials.",
      "type": "fatal"
    }
  ]
}

QRADAR_HEALTH_RESPONSE = [
    "42c7f297-b383-4e70-9964-40ea6a1aed51",
    "107d5dc6-fbb8-43a5-8faa-df8e37114476",
    "ff4e5ee4-b5d7-44c8-882a-e3acb8798e38",
    "27cab667-8c99-42a3-aa23-d91370e32fdc",
    "a920f6f0-c904-435d-8195-60f8634b4d2b",
]

QRADAR_500_ERROR_RESPONSE = {
    "error": {
        "type": "Server Error",
        "code": "500",
        "message": "Internal Error"
    }
}

QRADAR_OBSERVE_RESPONSES_FOR_POST = [
    {"search_id": "123", "status": "COMPLETED"},
    {"search_id": "456", "status": "COMPLETED"}
]

QRADAR_OBSERVE_RESPONSES_FOR_GET = [
    {
        "columns": [
            {"name": "destinationip"},
            {"name": "sourceip"}
        ]
    },
    {
        "events": [
            {
                "starttime": 1616354520581,
                "protocolid": 255,
                "sourceip": "10.6.1.110",
                "destinationip": "127.0.0.1",
                "sourcev6": "0:0:0:0:0:0:0:0",
                "sourcemac": "00:00:00:00:00:00",
                "username": None,
                "logsource_name": "System Notification-2 :: vm123",
                "event_descr": "General information message."
            },
            {
                "starttime": 1616354520581,
                "sourceip": "10.6.1.110",
                "destinationip": "127.0.0.1",
                "sourcev6": "0:0:0:0:0:0:0:0",
                "sourcemac": "00:00:00:00:00:00",
                "username": None,
                "logsource_name": "System Notification :: vm123",
                "event_descr": "General information message."
            }
        ]
    }
]


EXPECTED_WATCHDOG_ERROR = {
    'errors': [
        {
            'code': 'health check failed',
            'message': 'Invalid Health Check',
            'type': 'fatal'
        }
    ]
}
