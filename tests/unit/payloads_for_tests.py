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
      "message": "The request is missing a valid credentials.",
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
