# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest

from mock import Mock
from hamcrest import assert_that, has_entries

from xivo_confd.plugins.device.funckey import FuncKeyConverter

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.resources.func_key.model import FuncKey


class FuncKeyTestConverter(FuncKeyConverter):

    def build(self, user, line, position, funckey):
        pass


class TestFuncKeyConverter(unittest.TestCase):

    def setUp(self):
        self.converter = FuncKeyTestConverter()

    def test_no_label_returns_empty_string(self):
        line = Mock(Line, device_slot=1)
        funckey = Mock(FuncKey,
                       label=None,
                       blf=True)

        converted = self.converter.provd_funckey(line, 1, funckey, '1234')
        assert_that(converted, has_entries({1: has_entries(label="")}))

    def test_label_removes_invalid_characters(self):
        line = Mock(Line, device_slot=1)
        funckey = Mock(FuncKey,
                       label="\nhe;l\tlo\r",
                       blf=True)

        converted = self.converter.provd_funckey(line, 1, funckey, '1234')
        assert_that(converted, has_entries({1: has_entries(label="hello")}))
