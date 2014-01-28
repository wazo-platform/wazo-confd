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
import json
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_restapi.resources.line_extension.formatter import LineExtensionFormatter


class TestLineExtensionFormatter(unittest.TestCase):

    def test_to_model(self):
        line_id = 1
        extension_id = 2
        data = {'extension_id': extension_id}
        encoded_data = json.dumps(data)

        expected = LineExtension(line_id=line_id, extension_id=extension_id)

        formatter = LineExtensionFormatter()
        result = formatter.to_model(encoded_data, line_id)

        assert_that(result, equal_to(expected))
