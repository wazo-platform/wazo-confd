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
from mock import Mock

from xivo_dao.resources.voicemail.model import Voicemail
from xivo_confd.resources.voicemails.services import VoicemailService


class TestVoicemailService(unittest.TestCase):

    def setUp(self):
        self.sysconf = Mock()
        self.dao = Mock()
        self.validator = Mock()
        self.notifier = Mock()
        self.service = VoicemailService(self.dao, self.validator, self.notifier, self.sysconf)
        self.voicemail = Voicemail(number='1000', context='default')

    def test_when_editing_then_validation_passes(self):
        self.service.edit(self.voicemail)

        self.validator.validate_edit.assert_called_once_with(self.voicemail)

    def test_when_editing_then_dao_updated(self):
        self.service.edit(self.voicemail)

        self.dao.edit.assert_called_once_with(self.voicemail)

    def test_when_editing_then_notifier_notified(self):
        self.service.edit(self.voicemail)

        self.notifier.edited.assert_called_once_with(self.voicemail)

    def test_given_number_and_context_have_not_changed_when_editing_then_sysconfd_not_called(self):
        self.dao.get.return_value = self.voicemail

        self.service.edit(self.voicemail)

        self.assertEquals(self.sysconf.move_voicemail.call_count, 0)

    def test_given_number_and_context_have_changed_when_editing_then_sysconfd_called(self):
        old_voicemail = self.dao.get.return_value = Voicemail(number='100', context='ctx')

        self.service.edit(self.voicemail)

        self.sysconf.move_voicemail.assert_called_once_with(old_voicemail.number,
                                                            old_voicemail.context,
                                                            self.voicemail.number,
                                                            self.voicemail.context)

    def test_when_deleting_then_validation_passes(self):
        self.service.delete(self.voicemail)

        self.validator.validate_delete.assert_called_once_with(self.voicemail)

    def test_when_deleting_then_dao_updated(self):
        self.service.delete(self.voicemail)

        self.dao.delete.assert_called_once_with(self.voicemail)

    def test_when_deleting_then_notifier_notified(self):
        self.service.delete(self.voicemail)

        self.notifier.deleted.assert_called_once_with(self.voicemail)

    def test_when_deleting_a_voicemail_then_voicemail_storage_deleted(self):
        self.service.delete(self.voicemail)

        self.sysconf.delete_voicemail.assert_called_once_with(self.voicemail.number,
                                                              self.voicemail.context)
