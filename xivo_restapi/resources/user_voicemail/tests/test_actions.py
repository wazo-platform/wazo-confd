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
from xivo_dao.data_handler.user_voicemail.exception import UserVoicemailNotExistsError
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
            "enabled": True,
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

        user_voicemail = UserVoicemail(user_id=user_id, voicemail_id=voicemail_id, enabled=True)
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

    @patch('xivo_dao.data_handler.user_voicemail.services.get_by_user_id')
    def test_get_voicemail_associated_to_a_user_with_no_voicemail(self, user_voicemail_get_by_user_id):
        user_id = 1
        expected_status_code = 404
        expected_result = ['User with id=%s does not have a voicemail' % user_id]

        user_voicemail_get_by_user_id.side_effect = UserVoicemailNotExistsError.from_user_id(user_id)

        result = self.app.get(BASE_URL % user_id)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_voicemail.services.get_by_user_id')
    def test_get_voicemail_associated_to_a_user(self, user_voicemail_get_by_user_id):
        user_id = 1
        voicemail_id = 13
        expected_status_code = 200
        expected_result = {
            u'voicemail_id': 13,
            u'user_id': 1,
            u'enabled': True,
            u'links': [
                {u'href': u'http://localhost/1.1/voicemails/%d' % voicemail_id,
                 u'rel': u'voicemails'},
                {u'href': u'http://localhost/1.1/users/%d' % user_id,
                 u'rel': u'users'}
            ]
        }

        user_voicemail_link = UserVoicemail(voicemail_id=voicemail_id,
                                            user_id=user_id)

        user_voicemail_get_by_user_id.return_value = user_voicemail_link

        result = self.app.get(BASE_URL % user_id)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_voicemail.services.get_by_user_id')
    @patch('xivo_dao.data_handler.user_voicemail.services.dissociate')
    def test_dissociate_voicemail(self, user_voicemail_dissociate, get_by_user_id):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)
        get_by_user_id.return_value = user_voicemail

        expected_status_code = 204
        expected_data = ''

        result = self.app.delete(BASE_URL % user_voicemail.user_id)

        get_by_user_id.assert_called_once_with(user_voicemail.user_id)
        user_voicemail_dissociate.assert_called_once_with(user_voicemail)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_data))

    @patch('xivo_dao.data_handler.user_voicemail.services.get_by_user_id')
    @patch('xivo_dao.data_handler.user_voicemail.services.dissociate')
    def test_dissociate_voicemail_no_user(self, user_voicemail_dissociate, get_by_user_id):
        user_id = 1

        expected_status_code = 404
        expected_result = ['User with id=%s does not have a voicemail' % user_id]

        get_by_user_id.side_effect = UserVoicemailNotExistsError.from_user_id(user_id)

        result = self.app.delete(BASE_URL % user_id)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))
