wazo-confd
==========

[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=wazo-confd)](https://jenkins.wazo.community/job/wazo-confd)

XiVO CONFD is a web server that provides a [RESTful](http://en.wikipedia.org/wiki/Representational_state_transfer)
service for configuring and managing a Wazo server. Further details on how to use the API can be found on
the [Wazo API web site](http://api.wazo.community)


Installing wazo-confd
---------------------

The server is already provided as a part of [Wazo](http://documentation.wazo.community).
Please refer to [the documentation](http://documentation.wazo.community/en/stable/installation/installsystem.html) for
further details on installing one.


Running unit tests
------------------

```
apt-get install libpq-dev python-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py27
```

Running integration tests
-------------------------

You need Docker installed.

```
cd integration_tests
pip install -U -r test-requirements.txt
make test-setup
make test
```


Development
-----------

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

In case you need to mount libraries (xivo-dao, xivo-bus, lib-python) inside the wazo-confd container:

1. Uncomment the confd volumes in ```integration_tests/assets/docker-compose.yml```
2. Set the environment variable: ```export LOCAL_GIT_REPOS=/parent/directory/to/all/git/repos```
3. Execute the steps above to run integration tests


Profiling
=========

* ```pip install gprof2dot```
* ```apt-get install graphviz```
* set the `profile` directory configuration
* process file in directory with the following command:

```gprof2dot -f pstats <directory>/<file> | dot -Tpng -o output.png```
foobar
