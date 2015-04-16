# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from mock import patch, Mock
from hamcrest import assert_that, equal_to

from xivo_dao.resources.user_voicemail.model import UserVoicemail
from xivo_dao.resources.user_voicemail import services as user_voicemail_services


class TestUserVoicemail(unittest.TestCase):

    @patch('xivo_dao.resources.user_voicemail.validator.validate_association')
    @patch('xivo_dao.resources.user_voicemail.dao.associate')
    @patch('xivo_dao.resources.user_voicemail.notifier.associated')
    def test_associate(self, notifier_associated, dao_associate, validate_association):
        user_voicemail = Mock(UserVoicemail)

        result = user_voicemail_services.associate(user_voicemail)

        assert_that(result, equal_to(user_voicemail))
        validate_association.assert_called_once_with(user_voicemail)
        dao_associate.assert_called_once_with(user_voicemail)
        notifier_associated.assert_called_once_with(user_voicemail)

    @patch('xivo_dao.resources.user_voicemail.dao.get_by_user_id')
    def test_get_by_user_id(self, user_voicemail_get_by_user_id):
        user_id = 123
        voicemail_id = 42
        expected_result = UserVoicemail(user_id=user_id,
                                        voicemail_id=voicemail_id)
        user_voicemail_get_by_user_id.return_value = UserVoicemail(user_id=user_id,
                                                                   voicemail_id=voicemail_id)

        result = user_voicemail_services.get_by_user_id(user_id)

        user_voicemail_get_by_user_id.assert_called_once_with(user_id)
        assert_that(result, equal_to(expected_result))

    @patch('xivo_dao.resources.user_voicemail.dao.find_by_user_id')
    def test_find_by_user_id(self, user_voicemail_find_by_user_id):
        user_id = 123
        voicemail_id = 42
        expected_result = UserVoicemail(user_id=user_id,
                                        voicemail_id=voicemail_id)
        user_voicemail_find_by_user_id.return_value = UserVoicemail(user_id=user_id,
                                                                    voicemail_id=voicemail_id)

        result = user_voicemail_services.find_by_user_id(user_id)

        user_voicemail_find_by_user_id.assert_called_once_with(user_id)
        assert_that(result, equal_to(expected_result))

    @patch('xivo_dao.resources.user_voicemail.dao.find_by_voicemail_id')
    def test_find_by_voicemail_id(self, user_voicemail_find_by_voicemail_id):
        user_id = 123
        voicemail_id = 42
        expected_result = UserVoicemail(user_id=user_id,
                                        voicemail_id=voicemail_id)
        user_voicemail_find_by_voicemail_id.return_value = UserVoicemail(user_id=user_id,
                                                                         voicemail_id=voicemail_id)

        result = user_voicemail_services.find_by_voicemail_id(voicemail_id)

        user_voicemail_find_by_voicemail_id.assert_called_once_with(voicemail_id)
        assert_that(result, equal_to(expected_result))

    @patch('xivo_dao.resources.user_voicemail.dao.dissociate')
    @patch('xivo_dao.resources.user_voicemail.notifier.dissociated')
    @patch('xivo_dao.resources.user_voicemail.validator.validate_dissociation')
    def test_dissociate(self, validate_dissociation, notifier_dissociated, dao_dissociate):
        user_voicemail = Mock(UserVoicemail)

        user_voicemail_services.dissociate(user_voicemail)

        validate_dissociation.assert_called_once_with(user_voicemail)
        dao_dissociate.assert_called_once_with(user_voicemail)
        notifier_dissociated.assert_called_once_with(user_voicemail)
