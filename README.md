XiVO CONFD
=============

[![Build Status](https://travis-ci.org/xivo-pbx/xivo-confd.png?branch=master)](https://travis-ci.org/xivo-pbx/xivo-confd)

XiVO CONFD is a web server that provides a [RESTful](http://en.wikipedia.org/wiki/Representational_state_transfer)
service for configuring and managing a XiVO server. Further details on how to use the API can be found on
the [XiVO documentation web site](http://documentation.xivo.io/production/api_sdk/rest_api/rest_api.html)


Installing CONFD
-------------------

The server is already provided as a part of [XiVO](http://documentation.xivo.io).
Please refer to [the documentation](ttp://documentation.xivo.io/production/installation/installsystem.html) for
further details on installing one.

Running unit tests
------------------

1. Install requirements with ```pip install -r requirements.txt```
2. Run tests with ```nosetests xivo_confd```


Running functional tests
------------------------

1. [XiVO acceptance](https://github.com/xivo-pbx/xivo-acceptance)
2. ```
cd integration_tests
make test-setup
make test-image
nosetests
```

In case you need to mount xivo_dao inside the xivo-confd container, add the
following line in confd volumes in
integration_tests/assets/base/docker-compose.yml

```
- "/path/to/xivo_dao:/usr/local/lib/python2.7/site-packages/xivo_dao"
```

If you need to run tests more than once (e.g. when developing):

```
make stop test-image start
DOCKER=0 nosetests suite
```
