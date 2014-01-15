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

from mock import patch
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.cti_profile.model import CtiProfile
from xivo_restapi.helpers.tests.test_resources import TestResources

BASE_URL = "1.1/cti_profiles"


class TestDeviceActions(TestResources):

    @patch('xivo_dao.data_handler.cti_profile.services.find_all')
    def test_list(self, profile_service_list):
        expected_status_code = 200
        expected_result = {
                    'total': 2,
                    'items': [
                        {
                            'id': 1,
                            'name': 'Client',
                            'links': [{
                                            'href': 'http://localhost/1.1/cti_profiles/1',
                                            'rel': 'cti_profiles'
                                        }]
                        },
                        {
                            "id": 2,
                            "name": "Agent",
                            'links': [{
                                            'href': 'http://localhost/1.1/cti_profiles/2',
                                            'rel': 'cti_profiles'
                                        }]
                        }
                    ]
                }
        profile1 = CtiProfile(id=1, name="Client")
        profile2 = CtiProfile(id=2, name="Agent")
        profile_service_list.return_value = [profile1, profile2]

        result = self.app.get(BASE_URL)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))
