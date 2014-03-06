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

from xivo_restapi.v1_0.service_data_model.base_sdm import BaseSdm
import unittest
from xivo_restapi.v1_0.service_data_model.sdm_exception import IncorrectParametersException


class TestBaseSdm(unittest.TestCase):

    def test_todict(self):
        base_instance = BaseSdm()
        base_instance.attr1 = 'val1'
        base_instance.attr2 = 2
        base_instance.attr3 = None
        second_instance = BaseSdm()
        second_instance.my_attr = 'hello'
        base_instance.attr4 = second_instance
        base_instance.attr5 = [second_instance]
        expected_result = {'attr1': 'val1',
                           'attr2': 2,
                           'attr3': None,
                           'attr4': {'my_attr': 'hello'},
                           'attr5': [{'my_attr': 'hello'}]}

        result = base_instance.todict()
        self.assertEquals(result, expected_result)

    def test_validate_success(self):
        base_instance = BaseSdm()
        base_instance.attr1 = 'val1'
        base_instance.attr2 = 2
        base_instance.attr3 = None

        data = {'attr3': None,
                'attr2': 'value2'}
        self.assertTrue(base_instance.validate(data))

    def test_validate_fail(self):
        base_instance = BaseSdm()
        base_instance.attr1 = 'val1'
        base_instance.attr2 = 2
        base_instance.attr3 = None

        data = {'attr11': 1,
                'attr': 'value2',
                'attr3': None}
        try:
            base_instance.validate(data)
        except IncorrectParametersException as e:
            self.assertEqual(str(e), 'Incorrect parameters sent: attr11, attr')
            return

        self.assertTrue(False, 'Exception not raised!')
