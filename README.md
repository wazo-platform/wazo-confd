<p align="center"><img src="https://github.com/wazo-platform/wazo-platform.org/raw/master/static/images/logo.png" height="200"></p>

# wazo-confd

[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=wazo-confd)](https://jenkins.wazo.community/job/wazo-confd)

wazo-confd is a micro-service that provides a [RESTful](http://en.wikipedia.org/wiki/Representational_state_transfer)
API for configuring and managing a Wazo server. Further details on how to use the API can be found on
the [Wazo API documentation](https://wazo-platform.org/documentation)

## Installing wazo-confd

The server is already provided as a part of [Wazo Platform](https://wazo-platform.org/uc-doc/).
Please refer to [the documentation](https://wazo-platform.org/uc-doc/installation/install-system) for
further details on installing one.

## Usage

Launching wazo-confd

```sh
wazo-confd [--user <user>] --config-file <path/to/config/file>
```

On a Wazo Platform environment, wazo-confd is launched automatically at system boot via a systemd service.

## Testing

### Running unit tests

```sh
apt-get install libpq-dev python-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py311
```

### Running integration tests

You need Docker installed.

```sh
cd integration_tests
pip install -U -r test-requirements.txt
make test-setup
make test
```

### Profiling

* ```pip install gprof2dot```
* ```apt-get install graphviz```
* set the `profile` directory configuration
* process file in directory with the following command:

```gprof2dot -f pstats <directory>/<file> | dot -Tpng -o output.png```

### openapi specification

The openapi specification of the API is constructed, at wazo-confd startup, from the per-plugin yaml files `wazo_confd/plugins/*/api.yml`, and made available under the `/api` endpoint.
To build and share the full specification without having to rely on deploying and querying wazo-confd API, see [helper tool in wazo-tools](https://github.com/wazo-platform/wazo-tools/tree/master/openapi-synthesize)

## Development

### Modified database

You need the repos xivo-manage-db up-to-date.

1. ```git clone https://github.com/wazo-platform/xivo-manage-db```
2. ```MANAGE_DB_DIR=../../xivo-manage-db make update-db```
3. Execute the steps above to run integration tests

### Modified wazo-provd

You need the repos wazo-provd up-to-date.

1. ```git clone https://github.com/wazo-platform/wazo-provd```
2. ```PROVD_DIR=../../wazo-provd make build-provd```
3. Execute the steps above to run integration tests

### Mounting libraries

In case you need to mount libraries (xivo-dao, wazo-bus, lib-python) inside the wazo-confd container:

1. Uncomment the confd volumes in ```integration_tests/assets/docker-compose.yml```
2. Set the environment variable: ```export LOCAL_GIT_REPOS=/parent/directory/to/all/git/repos```
3. Execute the steps above to run integration tests

## How to get help

If you ever need help from the Wazo Platform community, the following resources are available:

* [Discourse](https://wazo-platform.discourse.group/)
* [Mattermost](https://mm.wazo.community)

## Contributing

You can learn more on how to contribute in the [Wazo Platform documentation](https://wazo-platform.org/contribute/code).

## License

wazo-confd is released under the GPL 3.0 license. You can get the full license in the [LICENSE](LICENSE) file.
