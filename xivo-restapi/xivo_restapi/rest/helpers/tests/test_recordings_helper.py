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
from mock import Mock
from xivo_dao.alchemy.recordings import Recordings
from xivo_restapi.rest.helpers import recordings_helper, global_helper
import unittest


class TestRecordingsHelper(unittest.TestCase):

    def test_supplement_add_input(self):
        data = {'champ1': '',
                'champ2': ''}
        expected_result = {'champ1': None,
                           'champ2': None}
        result = recordings_helper.supplement_add_input(data)
        self.assertTrue(expected_result == result)

    def test_create_instance(self):
        data = {'campaign_name': 'name'}
        global_helper.create_class_instance = Mock()
        mock_return_value = Mock()
        global_helper.create_class_instance.return_value = mock_return_value
        result = recordings_helper.create_instance(data)
        global_helper.create_class_instance.assert_called_with(Recordings, data)
        self.assertEqual(result, mock_return_value)
