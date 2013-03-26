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

from mock import patch
from xivo_restapi.rest import rest_encoder
from xivo_restapi.rest.helpers.exception_catcher import catch_exception
import unittest


class TestExceptionCatcher(unittest.TestCase):


    @patch("xivo_restapi.rest.helpers.exception_catcher.make_response")
    def test_catch_exception(self, patch_make_response):

        def raising(arg):
            raise Exception()
        def not_raising(arg):
            return arg

        decorated_raising = catch_exception(raising)
        decorated_raising("test")
        patch_make_response.assert_called_with(rest_encoder.encode(["An unexpected exception occured: "]), 500);

        decorated_not_raising = catch_exception(not_raising)
        result = decorated_not_raising("test")
        self.assertEquals(result, "test")
