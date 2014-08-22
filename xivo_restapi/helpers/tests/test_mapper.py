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

from xivo_restapi.helpers import mapper
from xivo_dao.data_handler.exception import InputError


class TestMapper(unittest.TestCase):

    def test_map_to_api(self):
        excpected_result = {
            "id": 1,
            "username": 'toto',
            "device_slot": 1,
            "provisioning_extension": 123456
        }

        data_dict = {
            'id': 1,
            'username': 'toto',
            'num': 1,
            'provisioningid': 123456
        }

        mapping_model_to_api = {
            'id': 'id',
            'username': 'username',
            'num': 'device_slot',
            'provisioningid': 'provisioning_extension',
        }

        result = mapper.map_to_api(mapping_model_to_api, data_dict)

        self.assertEqual(excpected_result, result)

    def test_map_to_model(self):
        excpected_result = {
            'id': 1,
            'username': 'toto',
            'num': 1,
            'provisioningid': 123456
        }

        data_dict = {
            "id": 1,
            "username": 'toto',
            "device_slot": 1,
            "provisioning_extension": 123456
        }

        mapping_model_to_api = {
            'id': 'id',
            'username': 'username',
            'num': 'device_slot',
            'provisioningid': 'provisioning_extension',
        }

        result = mapper.map_to_model(mapping_model_to_api, data_dict)

        self.assertEqual(excpected_result, result)

    def test_validate_data_from_api_with_valid_data(self):
        data_dict = {
            "api_key1": 1,
            "api_key2": 'toto',
            "api_key3": 1,
            "api_key4": 123456
        }

        mapping = {
            'model_key1': 'api_key1',
            'model_key2': 'api_key2',
            'model_key3': 'api_key3',
            'model_key4': 'api_key4',
        }

        mapper.validate_data_from_api(mapping, data_dict)

        # No exception raised

    def test_validate_data_from_api_with_invalid_data(self):
        data_dict = {
            "api_key1": 1,
            "api_key2": 'toto',
            "api_key3": 1,
            "api_key4": 123456,
            "invalid_key": 123456
        }

        mapping = {
            'model_key1': 'api_key1',
            'model_key2': 'api_key2',
            'model_key3': 'api_key3',
            'model_key4': 'api_key4',
        }

        self.assertRaises(InputError, mapper.validate_data_from_api, mapping, data_dict)
