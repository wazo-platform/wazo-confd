# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
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

import os
import requests
import pprint

from hamcrest import assert_that, empty

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase

ASSET_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')


class TestDocumentation(AssetLaunchingTestCase):

    assets_root = ASSET_ROOT
    service = 'confd'
    asset = 'documentation'

    def test_documentation_errors(self):
        api_url = 'https://confd:9486/1.1/api/api.json'
        self.validate_api(api_url)

    def validate_api(self, url):
        validator_url = u'http://localhost:18080/debug'
        response = requests.get(validator_url, params={'url': url})
        assert_that(response.json(), empty(), pprint.pformat(response.json()))
