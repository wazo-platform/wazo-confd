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

from xivo_restapi.rest.helpers.voicemails_helper import VoicemailsHelper
from xivo_restapi.services.utils.exceptions import IncorrectParametersException
import unittest


class TestVoicemailsHelper(unittest.TestCase):

    def setUp(self):
        self.helper = VoicemailsHelper()

    def test_validate_data_success(self):
        data = {'mailbox': '123',
                'fullname': 'test'}
        try:
            self.helper.validate_data(data)
        except:
            self.assertTrue(False, "An unexpected exception occured")
        self.assertTrue(True)

    def test_validate_data_failed(self):
        data = {'mailbox': '123',
                'fullname': 'test',
                'unexisting_field': 'value'}
        self.assertRaises(IncorrectParametersException, self.helper.validate_data, data)
