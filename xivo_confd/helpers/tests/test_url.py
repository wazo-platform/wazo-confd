# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
from mock import patch

from xivo_confd.helpers import url


class TestUrlCheckers(unittest.TestCase):

    @patch('xivo_confd.resources.user.services.get')
    def test_check_user_exists(self, user_get):
        url.check_user_exists(1)

        user_get.assert_called_once_with(1)

    @patch('xivo_confd.resources.line.services.get')
    def test_check_line_exists(self, line_get):
        url.check_line_exists(1)

        line_get.assert_called_once_with(1)

    @patch('xivo_confd.resources.extension.services.get')
    def test_check_extension_exists(self, extension_get):
        url.check_extension_exists(1)

        extension_get.assert_called_once_with(1)
