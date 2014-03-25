# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
from mock import patch, Mock
from hamcrest import assert_that, equal_to

from xivo_restapi.resources.func_keys import mapper


class TestMapper(unittest.TestCase):

    @patch('xivo_restapi.resources.func_keys.mapper.flask_helpers.url_for')
    def test_add_links_to_dict(self, url_for):
        url = url_for.return_value = 'http://url'
        func_key = Mock(id=1)

        expected = {
            'links': [
                {
                    'rel': 'func_keys',
                    'href': url,
                }
            ]
        }

        result = {}
        mapper.add_links_to_dict(result, func_key)

        assert_that(result, equal_to(expected))
        url_for.assert_called_once_with('.get', funckeyid=func_key.id, _external=True)
