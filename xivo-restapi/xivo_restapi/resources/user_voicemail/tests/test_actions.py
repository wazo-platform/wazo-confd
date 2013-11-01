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
from hamcrest import assert_that, equal_to

from mock import patch
from xivo_dao.data_handler.user_voicemail.model import UserVoicemail
from xivo_restapi.helpers.tests.test_resources import TestResources


BASE_URL = "/1.1/users/%s/voicemail"


class TestUserVoicemailActions(TestResources):

    @patch('xivo_restapi.resources.user_voicemail.actions.formatter')
    @patch('xivo_dao.data_handler.user_voicemail.services.associate')
    def test_associate_voicemail(self, user_voicemail_associate, formatter):
        user_id = 1
        voicemail_id = 2

        expected_status_code = 201
        expected_result = {
            "user_id": user_id,
            "voicemail_id": voicemail_id,
            "links": [
                {
                    "rel": "voicemails",
                    "href": "http://localhost/1.1/voicemails/%s" % voicemail_id
                },
                {
                    "rel": "users",
                    "href": "http://localhost/1.1/users/%s" % user_id
                }
            ]
        }

        user_voicemail = UserVoicemail(user_id=user_id, voicemail_id=voicemail_id)
        user_voicemail_associate.return_value = user_voicemail

        formatter.to_model.return_value = user_voicemail
        formatter.to_api.return_value = self._serialize_encode(expected_result)

        data = {
            'voicemail_id': voicemail_id
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL % user_id, data=data_serialized)

        formatter.to_model.assert_called_once_with(data_serialized, user_id)
        user_voicemail_associate.assert_called_once_with(user_voicemail)
        formatter.to_api.assert_called_once_with(user_voicemail)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))