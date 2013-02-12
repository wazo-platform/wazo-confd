# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from mock import Mock, patch
from xivo_restapi.rest import rest_encoder
import unittest
from xivo_dao.alchemy.recordings import Recordings


class SampleClass:
    id = 1
    _privateFoo = 2
    __privateBar = 3
    foo = 4
    bar = 5
    other = 6

    def __init__(self, privateFoo, privateBar, foo, bar, other):
        self.id = 1
        self._privateFoo = privateFoo
        self.__privateBar = privateBar
        self.foo = foo
        self.bar = bar
        self.other = other


class TestRestEncoder(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_process_paginated_data(self):
        obj1 = Recordings()
        obj2 = Recordings()
        my_tuple = (2, [obj1, obj2])
        data = {'total': 2,
                'data': [obj1, obj2]}
        result = rest_encoder._process_paginated_data(my_tuple)
        self.assertEqual(result, data)

    def test_encode_tuple(self):
        obj1 = Recordings()
        data = (1, [obj1])
        result = rest_encoder.encode(data)
        expected_result = {u'total': 1,
                           u'data': [{u'cid': None,
                                      u'start_time': None,
                                      u'caller': None,
                                      u'campaign_id': None,
                                      u'filename': None,
                                      u'end_time': None,
                                      u'client_id': None,
                                      u'callee': None,
                                      u'agent_id': None}]}
        self.assertEqual(rest_encoder.decode(result), expected_result)
