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

from mock import patch
from xivo_dao.data_handler.user_voicemail.model import UserVoicemail
from xivo_restapi.helpers.tests.test_resources import TestResources


BASE_URL = "/1.1/users/%s/voicemail"


@patch('xivo_restapi.helpers.url.check_user_exists')
class TestUserVoicemailActions(TestResources):

    def build_item(self, user_voicemail):
        item = {
            "user_id": user_voicemail.user_id,
            "voicemail_id": user_voicemail.voicemail_id,
            "enabled": user_voicemail.enabled,
            "links": [
                {
                    "rel": "voicemails",
                    "href": "http://localhost/1.1/voicemails/%s" % user_voicemail.voicemail_id
                },
                {
                    "rel": "users",
                    "href": "http://localhost/1.1/users/%s" % user_voicemail.user_id
                }
            ]
        }

        return item

    @patch('xivo_dao.data_handler.user_voicemail.services.associate')
    def test_associate_voicemail(self, user_voicemail_associate, user_exists):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2, enabled=True)
        user_voicemail_associate.return_value = user_voicemail

        expected_result = self.build_item(user_voicemail)

        data = {'voicemail_id': user_voicemail.voicemail_id}
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL % user_voicemail.user_id, data=data_serialized)

        self.assert_response_for_create(result, expected_result)
        user_exists.assert_called_once_with(user_voicemail.user_id)
        user_voicemail_associate.assert_called_once_with(user_voicemail)

    @patch('xivo_dao.data_handler.user_voicemail.services.get_by_user_id')
    def test_get_voicemail_associated_to_a_user(self, user_voicemail_get_by_user_id, user_exists):
        user_voicemail = UserVoicemail(voicemail_id=1,
                                       user_id=2)
        user_voicemail_get_by_user_id.return_value = user_voicemail

        expected_result = self.build_item(user_voicemail)

        result = self.app.get(BASE_URL % user_voicemail.user_id)

        self.assert_response_for_get(result, expected_result)
        user_exists.assert_called_once_with(user_voicemail.user_id)

    @patch('xivo_dao.data_handler.user_voicemail.services.get_by_user_id')
    @patch('xivo_dao.data_handler.user_voicemail.services.dissociate')
    def test_dissociate_voicemail(self, user_voicemail_dissociate, get_by_user_id, user_exists):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)
        get_by_user_id.return_value = user_voicemail

        result = self.app.delete(BASE_URL % user_voicemail.user_id)

        self.assert_response_for_delete(result)
        user_exists.assert_called_once_with(user_voicemail.user_id)
        get_by_user_id.assert_called_once_with(user_voicemail.user_id)
        user_voicemail_dissociate.assert_called_once_with(user_voicemail)
