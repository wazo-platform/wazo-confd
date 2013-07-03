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

import unittest
from xivo_restapi.helpers import serializer


class TestSerializer(unittest.TestCase):

    def test_encode(self):
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
        self.assertEqual(serializer.decode(result), data)
