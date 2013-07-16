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
from xivo_restapi.resources.users import mapper
from xivo_dao.data_handler.user.model import User


class TestMapper(unittest.TestCase):

    def test_encode_list(self):
        obj1 = User(id=1, firstname='User', lastname='1')
        obj2 = User(id=2, firstname='User', lastname='2')
        data = [obj1, obj2]

        excpected_result = '{"items": [{"lastname": "1", "id": 1, "firstname": "User"}, {"lastname": "2", "id": 2, "firstname": "User"}], "total": 2}'

        result = mapper.encode_list(data)

        self.assertEqual(excpected_result, result)

    def test_encode(self):
        data = User(id=1, firstname='User', lastname='1')

        excpected_result = '{"lastname": "1", "id": 1, "firstname": "User"}'

        result = mapper.encode_user(data)

        self.assertEqual(excpected_result, result)
