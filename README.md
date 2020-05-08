# IBM QRadar Relay API

The API itself is just a simple Flask (WSGI) 
created to obtain raw logs from IBM QRadar for a specified
time period containing given observables.


## Installation
To install the application,
open the project folder in the terminal and run the following commands:
```bash
python3 -m venv python_venv
```
- For POSIX Platform:
```bash
. python_venv/bin/activate
```
- For Windows Platform:
```bash
venv_python\Scripts\activate.bat
```
Then install requirements: 
```bash
pip install -U -r requirements.txt
```

## Testing

```bash
pip install -U -r test-requirements.txt
```

- Check for *PEP 8* compliance: `flake8 .`.
- Run the suite of unit tests: `pytest -v tests/unit/`.

## Details
The IBM QRadar Relay API implements the following list of endpoints:
* `/observe/observables`,
* `/health`.

Other endpoints (`/refer/observables`, `/respond/observables`,
`/respond/trigger`, `/deliberate/observables`) 
returns empty responses.

**Note**: currently, the `/observe/observables` endpoint does
not return data in the CTIM format. Instead, raw logs from IBM QRadar are returned.

## Usage
```bash
pip install -U -r use-requirements.txt
```
Export your Flask server URL, SECRET_KEY which was used to generate
JWT token, and SERVER_IP of IBM QRadar application.
```bash
export URL=<...>
export JWT=<...>
export SECRET_KEY=<...>
export SERVER_IP=<...>
```
Run your Flask app.
```bash
python3 app.py
```
Now IBM QRadar Relay API is ready to be used.
```bash
http POST "${URL}"/health Authorization:"Bearer ${JWT}"
http POST "${URL}"/observe/observables Authorization:"Bearer ${JWT}" < observables.json
```

## JWT Structure

- Header
```json
{
  "alg": "HS256"
}
```

- Payload
```json
{
    "user": "<Username for IBM QRadar>",
    "pass": "<Password for IBM QRadar>"
}
```

# Workflow of obtaining raw logs

Suppose we got observable: ```[{"type": "url", "value": "cpi-istanbul.com"}]```.
1. We initiate a search for one event and get its search_id. 
In order to do that we do POST - `/ariel/searches` where the parameter
query_expression contains query ```SELECT * FROM events LIMIT 1```

    Received payload:
    ```
    {
      "cursor_id": "8aa7575f-da92-4d47-9d2e-0e833a66b202",
      "status": "WAIT",
                 ...
        [ Some of the lines were deleted ]
                 ...
      "search_id": "8aa7575f-da92-4d47-9d2e-0e833a66b202"
    }
    ```
2. Then we send a GET request to `ariel/searches/{search_id}/metadata` to retrieve
the columns that are defined for the specified Ariel search id.
 It takes about 2 sec for an additional request when we want to receive all column names.

    Received payload:
    ```
    {
      "columns": [
        {
          "name": "ACF2 rule key"
        },
        {
          "name": "starttime"
        },
        {
          "name": "tlvs"
        },
                     ...
            [ Some of the lines were deleted ]
                     ...
        {
          "name": "username"
        },
        {
          "name": "FireEye_URL_property"
        },
        {
          "name": "URL"
        }
      ]
    }
    ```

3. Now we know what column names are in the database and we can choose among them those that contain the type of our observables.

    Result: ``` [“FireEye_URL_property", "URL”] ```

     We check each column name for observable type name occurrence: FireEye_URL_property —> fireeye_url_property —> we find the word 'url' in our string, so it’s a suitable column.
     We make the first search to get all column names and then choose a set of names for each observable separately. After that we put pairs (<column_name>=<observable_value>) to the query for QRadar search.
     So we make one request for all observables, because we think it’s better in terms of performance. 

 4. We get raw logs with a filter on the fields that we received from the previous step.
 In order to do that we do POST - `/ariel/searches` with query
```SELECT UTF8(payload) FROM events WHERE FireEye_URL_property='cpi-istanbul.com' OR URL='cpi-istanbul.com’```
    
    Received payload:
   ```
    {
    "events": [
        {
            "utf8_payload": "<182>Apr 28 13:38:25 redhat1 CEF:0|Trend Micro|Control Manager|7.0|FH:Log|Suspicious Files|3|deviceExternalId=1 rt=Nov 15 2016 02:47:21 GMT+00:00 ip=178.250.45.14  domain=cpi-istanbul.com url=cpi-istanbul.com email=test@i.ua hostname=some.test.host mac_address=30-65-EC-6F-C4-58 file_name=testName.txt file_path=/opt/test/file/path fileHash=D6712CAE5EC821F910E14945153AE7871AA536CA sha256=01468b1d3e089985a4ed255b6594d24863cfd94a647329c631e4f4e52759f8a9 sha1=cf23df2207d99a74fbe169e3eba035e633b65d94  md5=1BC29B36F623BA82AAF6724FD3B16718  cn3=1"
        },
        {
            "utf8_payload": "<182>Apr 28 13:38:35 redhat1 CEF:0|Trend Micro|Control Manager|7.0|FH:Log|Suspicious Files|3|deviceExternalId=1 rt=Nov 15 2016 02:47:21 GMT+00:00 ip=178.250.45.14  domain=cpi-istanbul.com url=cpi-istanbul.com email=test@i.ua hostname=some.test.host mac_address=30-65-EC-6F-C4-58 file_name=testName.txt file_path=/opt/test/file/path fileHash=D6712CAE5EC821F910E14945153AE7871AA536CA sha256=01468b1d3e089985a4ed255b6594d24863cfd94a647329c631e4f4e52759f8a9 sha1=cf23df2207d99a74fbe169e3eba035e633b65d94  md5=1BC29B36F623BA82AAF6724FD3B16718  cn3=1"
        },
                     ...
            [ Some of the lines were deleted ]
                     ...
        {
            "utf8_payload": "<182>Apr 28 13:38:35 redhat1 CEF:0|Trend Micro|Control Manager|7.0|FH:Log|Suspicious Files|3|deviceExternalId=1 rt=Nov 15 2016 02:47:21 GMT+00:00 ip=178.250.45.14  domain=cpi-istanbul.com url=cpi-istanbul.com email=test@i.ua hostname=some.test.host mac_address=30-65-EC-6F-C4-58 file_name=testName.txt file_path=/opt/test/file/path fileHash=D6712CAE5EC821F910E14945153AE7871AA536CA sha256=01468b1d3e089985a4ed255b6594d24863cfd94a647329c631e4f4e52759f8a9 sha1=cf23df2207d99a74fbe169e3eba035e633b65d94  md5=1BC29B36F623BA82AAF6724FD3B16718  cn3=1"
        },
        {
            "utf8_payload": "<182>Apr 28 13:38:55 redhat1 CEF:0|Trend Micro|Control Manager|7.0|FH:Log|Suspicious Files|3|deviceExternalId=1 rt=Nov 15 2016 02:47:21 GMT+00:00 ip=178.250.45.14  domain=cpi-istanbul.com url=cpi-istanbul.com email=test@i.ua hostname=some.test.host mac_address=30-65-EC-6F-C4-58 file_name=testName.txt file_path=/opt/test/file/path fileHash=D6712CAE5EC821F910E14945153AE7871AA536CA sha256=01468b1d3e089985a4ed255b6594d24863cfd94a647329c631e4f4e52759f8a9 sha1=cf23df2207d99a74fbe169e3eba035e633b65d94  md5=1BC29B36F623BA82AAF6724FD3B16718  cn3=1"
        }
    ]
    }
   ```
