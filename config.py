from datetime import timedelta

from version import VERSION


class Config:
    VERSION = VERSION

    ARIAL_VERSION = '12.0'

    TOTAL_TIME_INTERVAL = timedelta(minutes=10)
    TIME_DELTA = timedelta(minutes=5)

    HEADERS = {
        'Accept': 'application/json',
        'Version': '12.0',
    }
    BASE_URI = '/api/'

    REFER_URL = (
        "https://{server_ip}/console/do/ariel/arielSearch?appName="
        "EventViewer&pageId=EventList&dispatch=performSearch"
        "&value(timeRangeType)=aqlTime&value(searchMode)=AQL&value(aql)="
        "SELECT * FROM events WHERE sourceip='{observable}' OR "
        "destinationip='{observable}' LAST 7 DAYS"
    )
