# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_restapi.resources.line_extension_collection.formatter import LineExtensionFormatter

LINE_ID = 1
EXTENSION_ID = 2


class TestLineExtensionFormatter(unittest.TestCase):

    def setUp(self):
        self.formatter = LineExtensionFormatter()

    def test_dict_to_model(self):
        data = {'extension_id': EXTENSION_ID}

        expected = LineExtension(line_id=LINE_ID, extension_id=EXTENSION_ID)

        result = self.formatter.dict_to_model(LINE_ID, data)

        assert_that(result, equal_to(expected))

    def test_model_from_ids(self):
        expected = LineExtension(line_id=LINE_ID, extension_id=EXTENSION_ID)

        result = self.formatter.model_from_ids(LINE_ID, EXTENSION_ID)

        assert_that(result, equal_to(expected))
