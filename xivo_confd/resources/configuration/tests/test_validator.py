# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from xivo_confd.resources.configuration import validator
from xivo_dao.helpers.exception import InputError


class TestValidator(unittest.TestCase):

    def test_validate_data_no_parameter(self):
        data = {}

        self.assertRaises(InputError, validator.validate_live_reload_data, data)

    def test_validate_data_enabled_is_none(self):
        data = {'enabled': None}

        self.assertRaises(InputError, validator.validate_live_reload_data, data)

    def test_validate_data_invalid_param(self):
        data = {'enabled': True,
                'foo': 'bar'}

        self.assertRaises(InputError, validator.validate_live_reload_data, data)
