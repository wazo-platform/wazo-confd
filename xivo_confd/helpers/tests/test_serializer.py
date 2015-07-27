# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import json
import unittest

from xivo_confd.helpers import serializer


class TestSerializer(unittest.TestCase):

    def test_encode(self):
        expected_result = '{"items": [{"lastname": "1", "id": 1, "firstname": "User"}, {"lastname": "2", "id": 2, "firstname": "User"}], "total": 2}'

        data = {
            'total': 2,
            'items': [
                {
                    "id": 1,
                    "firstname": "User",
                    "lastname": "1"
                },
                {
                    "id": 2,
                    "firstname": "User",
                    "lastname": "2"
                },
            ]
        }

        result = serializer.encode(data)

        self.assertEqual(json.loads(result), json.loads(expected_result))

    def test_decode(self):
        data = '{"items": [{"lastname": "1", "id": 1, "firstname": "User"}, {"lastname": "2", "id": 2, "firstname": "User"}], "total": 2}'

        expected_result = {
            'total': 2,
            'items': [
                {
                    "id": 1,
                    "firstname": "User",
                    "lastname": "1"
                },
                {
                    "id": 2,
                    "firstname": "User",
                    "lastname": "2"
                },
            ]
        }

        result = serializer.decode(data)

        self.assertEqual(result, expected_result)
