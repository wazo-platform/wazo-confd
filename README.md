XiVO confd
==========

[![Build Status](https://travis-ci.org/xivo-pbx/xivo-confd.png?branch=master)](https://travis-ci.org/xivo-pbx/xivo-confd)

XiVO CONFD is a web server that provides a [RESTful](http://en.wikipedia.org/wiki/Representational_state_transfer)
service for configuring and managing a XiVO server. Further details on how to use the API can be found on
the [XiVO API web site](http://api.xivo.io)


Installing xivo-confd
---------------------

The server is already provided as a part of [XiVO](http://documentation.xivo.io).
Please refer to [the documentation](ttp://documentation.xivo.io/production/installation/installsystem.html) for
further details on installing one.


Running unit tests
------------------

1. Install libffi ```apt-get install libffi-dev```
2. Install requirements with ```pip install -U -r requirements.txt -r test-requirements.txt```
3. Run tests with ```nosetests```


Running integration tests
-------------------------

You need the repos xivo-manage-db and xivo-provisioning.

To clone them:

```
git clone https://github.com/xivo-pbx/xivo-manage-db
git clone https://github.com/xivo-pbx/xivo-provisioning
```

If you already have them:

1. ensure they are up-to-date
2. change the values for ``PROVD_DIR`` and ``MANAGE_DB_DIR``

Run the tests:

```
cd integration_tests
pip install -U -r test-requirements.txt
make test-setup PROVD_DIR=../../xivo-provisioning MANAGE_DB_DIR=../../xivo-manage-db
make test
```


Development
-----------

In case you need to mount xivo_dao inside the xivo-confd container, add the
following line in confd volumes in
integration_tests/assets/base/docker-compose.yml

```
- "/path/to/xivo_dao:/usr/local/lib/python2.7/site-packages/xivo_dao"
```

If you need to run tests more than once (e.g. when developing):

```
make stop start
DOCKER=0 nosetests suite
```
