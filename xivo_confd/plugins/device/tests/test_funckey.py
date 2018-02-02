# -*- coding: UTF-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from hamcrest import assert_that, has_entries

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.resources.func_key.model import FuncKey

from ..funckey import FuncKeyConverter


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

    def test_invalid_chars_removed_from_label(self):
        line = Mock(Line, device_slot=1)
        funckey = Mock(FuncKey,
                       label="\nhe;l\tlo\r",
                       blf=True)

        converted = self.converter.provd_funckey(line, 1, funckey, '1234')
        assert_that(converted, has_entries({1: has_entries(label="hello")}))

    def test_invalid_chars_removed_from_value(self):
        line = Mock(Line, device_slot=1)
        funckey = Mock(FuncKey, blf=True, label=None)

        converted = self.converter.provd_funckey(line, 1, funckey, '\r1\t2;34\n')
        assert_that(converted, has_entries({1: has_entries(value="1234")}))
