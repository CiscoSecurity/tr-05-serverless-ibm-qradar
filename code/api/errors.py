INVALID_ARGUMENT = 'invalid argument'
PERMISSION_DENIED = 'permission denied'
UNKNOWN = 'unknown'
INTERNAL = 'internal error'
GATEWAY_TIMEOUT = 'gateway timeout'
AUTH_ERROR = 'authorization error'


class CTRBaseError(Exception):
    def __init__(self, code, message, type_='fatal'):
        super().__init__()
        self.code = code or UNKNOWN
        self.message = message or 'Something went wrong.'
        self.type_ = type_

    @property
    def json(self):
        return {'type': self.type_,
                'code': self.code,
                'message': self.message}


class QRadarInternalServerError(CTRBaseError):
    def __init__(self):
        super().__init__(
            INTERNAL,
            'The QRadar internal error.'
        )


class QRadarConnectionError(CTRBaseError):
    def __init__(self):
        super().__init__(
            GATEWAY_TIMEOUT,
            'The QRadar Relay timed out waiting for the response from API.'
        )


class QRadarInvalidCredentialsError(CTRBaseError):
    def __init__(self):
        super().__init__(
            PERMISSION_DENIED,
            'The request is missing valid credentials.'
        )


class AuthorizationError(CTRBaseError):
    def __init__(self, message='Authorization failed on QRadar side'):
        super().__init__(
            AUTH_ERROR,
            f'Authorization failed: {message}'
        )


class QRadarUnexpectedError(CTRBaseError):
    def __init__(self, response):
        if response.json():
            error_payload = response.json().get('message', '')
        super().__init__(
            UNKNOWN,
            error_payload or 'The QRadar API error.'
        )


class BadRequestError(CTRBaseError):
    def __init__(self, message):
        super().__init__(
            INVALID_ARGUMENT,
            f'Invalid JSON payload received. {message}'
        )


class WatchdogError(CTRBaseError):
    def __init__(self):
        super().__init__(
            code='health check failed',
            message='Invalid Health Check'
        )


class QRadarTimeoutError(CTRBaseError):
    def __init__(self):
        super().__init__(
            GATEWAY_TIMEOUT,
            'Failed to get search results since search processing '
            'is still ongoing on QRadar API side.'
        )


class InvalidArgumentError(CTRBaseError):
    def __init__(self, error):
        super().__init__(
            INVALID_ARGUMENT,
            str(error)
        )
