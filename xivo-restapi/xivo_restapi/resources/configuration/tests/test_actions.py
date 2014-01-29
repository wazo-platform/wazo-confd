# -*- coding: UTF-8 -*-

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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

from hamcrest import assert_that, equal_to
from mock import patch
from xivo_restapi.helpers.tests.test_resources import TestResources


BASE_URL = "/1.1/configuration"


class TestConfigurationActions(TestResources):

    @patch('xivo_dao.data_handler.configuration.services.get_live_reload_status')
    def test_get_live_reload_status(self, get_live_reload_status):
        expected_status_code = 200
        expected_result = {
            'enabled': True
        }

        get_live_reload_status.return_value = True

        result = self.app.get('%s/live_reload' % BASE_URL)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))
        get_live_reload_status.assert_called_once_with()

    @patch('xivo_dao.data_handler.configuration.services.set_live_reload_status')
    def test_edit_live_reload_status(self, set_live_reload_status):
        expected_status_code = 204
        data = {
            'enabled': False
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.put('%s/live_reload' % BASE_URL, data=data_serialized)

        assert_that(result.status_code, equal_to(expected_status_code))
        set_live_reload_status.assert_called_once_with(data)
