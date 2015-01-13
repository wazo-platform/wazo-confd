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
