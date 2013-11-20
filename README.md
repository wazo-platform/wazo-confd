XiVO REST API
=============

[![Build Status](https://travis-ci.org/xivo-pbx/xivo-restapi.png?branch=master)](https://travis-ci.org/xivo-pbx/xivo-restapi)

XiVO REST API is a web server that provides a [RESTful](http://en.wikipedia.org/wiki/Representational_state_transfer)
service for configuring and managing a XiVO server. Further details on how to use the API can be found on
the [XiVO documentation web site](http://documentation.xivo.fr/production/api_sdk/rest_api/rest_api.html)

Installing REST API
-------------------

The server is already provided as a part of [XiVO](http://documentation.xivo.fr).
Please refer to [the documentation](ttp://documentation.xivo.fr/production/installation/installsystem.html) for
further details on installing one.

Running unit tests
------------------

1. Install requirements with ```pip install -r requirements.txt```
2. Run tests with ```nosetests xivo-restapi/xivo_restapi```


Running functional tests
------------------------

1. Install and configure the [XiVO acceptance](https://github.com/xivo-pbx/xivo-acceptance) library
2. Go into ```xivo-restapi/acceptance/features_1_1```
3. Run any of the files with [lettuce](http://lettuce.it)
