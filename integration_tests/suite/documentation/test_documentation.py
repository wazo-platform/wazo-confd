# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals

import os
import requests
import pprint

from hamcrest import assert_that, empty

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase

requests.packages.urllib3.disable_warnings()

ASSET_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')


class TestDocumentation(AssetLaunchingTestCase):

    assets_root = ASSET_ROOT
    service = 'confd'
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
