[![Gitter Chat](https://img.shields.io/badge/gitter-join%20chat-brightgreen.svg)](https://gitter.im/CiscoSecurity/Threat-Response "Gitter Chat")

# QRadar Relay

A Cisco SecureX Concrete Relay implementation using QRadar as a third-party Cyber Threat Intelligence service provider.

The Relay itself is just a simple application written in Python that can be easily packaged and deployed.

## Rationale

- We need an application that will translate API requests from SecureX Threat Response to the third-party integration, and vice versa.
- We need an application that can be completely self contained within a virtualized container using Docker.

## Testing (Optional)

Open the code folder in your terminal.
```
cd code
```

If you want to test the application you will require Docker and several dependencies from the [requirements.txt](code/requirements.txt) file:
```
pip install --upgrade --requirement requirements.txt
```

You can perform two kinds of testing:

- Run static code analysis checking for any semantic discrepancies and [PEP 8](https://www.python.org/dev/peps/pep-0008/) compliance:

  `flake8 .`

- Run the suite of unit tests and measure the code coverage:
  `coverage run --source api/ -m pytest --verbose tests/unit/ && coverage report`
  
**NOTE.** If you need input data for testing purposes you can use data from the
[observables.json](code/observables.json) file.

### Building the Docker Container
In order to build the application, we need to use a `Dockerfile`.  

 1. Open a terminal.  Build the container image using the `docker build` command.

```
docker build -t tr-05-qradar .
```

 2. Once the container is built, and an image is successfully created, start your container using the `docker run` command and specify the name of the image we have just created.  By default, the container will listen for HTTP requests using port 9090.

```
docker run -dp 9090:9090 --name tr-05-qradar tr-05-qradar
```

 3. Watch the container logs to ensure it starts correctly.

```
docker logs tr-05-qradar
```

 4. Once the container has started correctly, open your web browser to http://localhost:9090.  You should see a response from the container.

    curl http://localhost:9090

## Implementation Details

This application was developed and tested under Python version 3.9.

### Implemented Relay Endpoints

- `POST /health`
  - Verifies the Authorization Bearer JWT and decodes it to restore the
  original credentials.
  - Authenticates to the underlying external service to check that the provided
  credentials are valid and the service is available at the moment.

- `POST /observe/observables`
  - Accepts a list of observables and filters out unsupported ones.
  - Verifies the Authorization Bearer JWT and decodes it to restore the
  original credentials.
  - Makes a series of requests to the underlying external service to query for
  some log data on each supported observable.
  - Maps the fetched data into appropriate CTIM entities.
  - Returns a list per each of the following CTIM entities (if any extracted):
    - `Sighting`.
  
- `POST /refer/observables`
  - Accepts a list of observables and filters out unsupported ones.
  - Builds a search link per each supported observable to pivot back to the
  QRadar console and look up event logs with the observable there.
  - Returns a list of those links.
  
- `POST /respond/observables`
  - Accepts a list of observables and filters out unsupported ones.
  - Verifies the Authorization Bearer JWT and decodes it to restore the
  original credentials.
  - Makes a series of requests to the underlying external service to query for
  actions available for given observables.
  - Returns a list of those actions.

- `POST /respond/trigger`
  - Accepts an observable and an action.
  - Verifies the Authorization Bearer JWT and decodes it to restore the
  original credentials.
  - Triggers an action at the underlying external service.
  - Returns an action result.

- `POST /version`
  - Returns the current version of the application.

### Supported Types of Observables

- `ip`

### CTIM Mapping Specifics

Each event log in response from the QRadar API for the IP observables generates the following CTIM entities:

- `Sightings` are based on the date and time the observable was seen in the logs and the log source that provided the event log.
