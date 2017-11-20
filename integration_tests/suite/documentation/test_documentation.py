# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import requests
import pprint

from hamcrest import assert_that, empty

from ..helpers.base import IntegrationTest

requests.packages.urllib3.disable_warnings()


class TestDocumentation(IntegrationTest):

    asset = 'documentation'

    def test_documentation_errors(self):
        confd_port = self.service_port(9486, 'confd')
        api_url = 'https://localhost:{port}/1.1/api/api.yml'.format(port=confd_port)
        api = requests.get(api_url, verify=False)
        self.validate_api(api)

    def validate_api(self, api):
        validator_port = self.service_port(8080, 'swagger-validator')
        validator_url = 'http://localhost:{port}/debug'.format(port=validator_port)
        response = requests.post(validator_url, data=api)
        assert_that(response.json(), empty(), pprint.pformat(response.json()))
