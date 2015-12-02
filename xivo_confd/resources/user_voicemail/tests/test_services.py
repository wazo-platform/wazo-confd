# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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
from mock import Mock, sentinel
from hamcrest import assert_that, equal_to

from xivo_dao.resources.user_voicemail.model import UserVoicemail

from xivo_confd.resources.user_voicemail.services import UserVoicemailService
from xivo_confd.helpers.validator import AssociationValidator


class TestUserVoicemailService(unittest.TestCase):

    def setUp(self):
        self.user_dao = Mock()
        self.voicemail_dao = Mock()
        self.user_voicemail_dao = Mock()
        self.notifier = Mock()
        self.validator = Mock(AssociationValidator)
        self.service = UserVoicemailService(self.user_dao,
                                            self.voicemail_dao,
                                            self.user_voicemail_dao,
                                            self.validator,
                                            self.notifier)

    def test_when_getting_parent_then_dao_is_called(self):
        expected_user_voicemail = self.user_voicemail_dao.get_by_user_id.return_value

        result = self.service.get_by_parent(sentinel.user_id)

        self.user_voicemail_dao.get_by_user_id.assert_called_once_with(sentinel.user_id)
        assert_that(result, equal_to(expected_user_voicemail))

    def test_when_listing_by_children_then_voicemail_dao_is_called(self):
        expected_user_voicemails = self.user_voicemail_dao.find_all_by_voicemail_id.return_value

        result = self.service.list_by_child(sentinel.voicemail_id)

        self.user_voicemail_dao.find_all_by_voicemail_id.assert_called_once_with(sentinel.voicemail_id)
        assert_that(result, equal_to(expected_user_voicemails))

    def test_when_validating_parent_then_user_dao_is_called(self):
        self.service.validate_parent(sentinel.user_id)

        self.user_dao.get.assert_called_once_with(sentinel.user_id)

    def test_when_validating_resource_then_voicemail_dao_is_called(self):
        self.service.validate_resource(sentinel.voicemail_id)

        self.voicemail_dao.get.assert_called_once_with(sentinel.voicemail_id)

    def test_when_associating_then_association_is_validated(self):
        association = Mock(UserVoicemail)
        self.service.associate(association)

        self.validator.validate_association.assert_called_once_with(association)

    def test_when_associating_then_dao_is_called(self):
        association = Mock(UserVoicemail)
        self.service.associate(association)

        self.user_voicemail_dao.associate.assert_called_once_with(association)

    def test_when_associating_then_notifier_is_called(self):
        association = Mock(UserVoicemail)
        self.service.associate(association)

        self.notifier.associated.assert_called_once_with(association)

    def test_when_dissociating_then_dissociation_is_validated(self):
        dissociation = Mock(UserVoicemail)
        self.service.dissociate(dissociation)

        self.validator.validate_dissociation.assert_called_once_with(dissociation)

    def test_when_dissociating_then_dao_is_called(self):
        dissociation = Mock(UserVoicemail)
        self.service.dissociate(dissociation)

        self.user_voicemail_dao.dissociate.assert_called_once_with(dissociation)

    def test_when_dissociating_then_notifier_is_called(self):
        dissociation = Mock(UserVoicemail)
        self.service.dissociate(dissociation)

        self.notifier.dissociated.assert_called_once_with(dissociation)
