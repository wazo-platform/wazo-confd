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

from xivo_dao.data_handler.cti_profile.model import CtiProfile
from xivo_restapi.helpers.tests.test_resources import TestResources

BASE_URL = "1.1/cti_profiles"


class TestCtiProfileActions(TestResources):

    def build_item(self, profile):
        return {'id': profile.id,
                'name': profile.name,
                'links': [{
                    'href': 'http://localhost/1.1/cti_profiles/%d' % profile.id,
                    'rel': 'cti_profiles'
                }]}

    @patch('xivo_dao.data_handler.cti_profile.services.find_all')
    def test_list(self, profile_service_list):
        profile1 = CtiProfile(id=1, name="Client")
        profile2 = CtiProfile(id=2, name="Agent")

        expected_result = {'total': 2,
                           'items': [self.build_item(profile1),
                                     self.build_item(profile2)]
                           }

        profile_service_list.return_value = [profile1, profile2]

        result = self.app.get(BASE_URL)

        self.assert_response_for_get(result, expected_result)

    @patch('xivo_dao.data_handler.cti_profile.services.get')
    def test_get(self, profile_service_get):
        profile = CtiProfile(id=1, name="Agent")
        profile_service_get.return_value = profile

        expected_result = self.build_item(profile)

        result = self.app.get('%s/%s' % (BASE_URL, 1))

        self.assert_response_for_get(result, expected_result)
        profile_service_get.assert_called_with(1)
