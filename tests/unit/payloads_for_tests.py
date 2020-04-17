EXPECTED_PAYLOAD_500_ERROR = {
  "errors": [
    {
      "code": "unknown",
      "message": "The QRadar API error.",
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
    "4e96d3b4-7107-4e94-a4ba-d63a3b6bad58",
    "64fc7210-938f-4d9c-b7cf-a13998018db7",
    "e368f26d-1a94-43d2-b590-1e6add2560ce",
    "e054e425-7ec7-40b6-9a2b-ac2fbb10dc71",
    "c53aed7c-ec83-43dd-9a53-a95b1cf6e4ab",
    "353363aa-723b-42a4-9968-4256cf48b796",
    "1055a8e7-0c71-45d0-b515-e80db8ae5db9",
    "42d15fc5-10e0-4571-9fa4-70e39558dcf1"
]

QRADAR_500_ERROR_RESPONSE = {
    "error": {
        "type": "Server Error",
        "code": "500",
        "message": "Internal Error"
    }
}
