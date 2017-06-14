# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

import unittest
import requests

from hamcrest import assert_that, equal_to
from xivo_test_helpers.confd.config import confd_base_url


class TestAuthentication(unittest.TestCase):

    def setUp(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers['Accept'] = 'application/json'

    def test_ignore_x_forwarded_for_header(self):
        url = confd_base_url() + '/infos'

        r = self.session.get(url, headers={'X-Forwarded-For': '127.0.0.1'})

        assert_that(r.status_code, equal_to(401))
