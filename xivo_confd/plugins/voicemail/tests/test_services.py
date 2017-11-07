# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_dao.alchemy.voicemail import Voicemail
from xivo_confd.plugins.voicemail.service import VoicemailService


class TestVoicemailService(unittest.TestCase):

    def setUp(self):
        self.sysconf = Mock()
        self.dao = Mock()
        self.validator = Mock()
        self.notifier = Mock()
        self.service = VoicemailService(self.dao, self.validator, self.notifier, self.sysconf)
        self.voicemail = Mock(Voicemail, number='1000', context='default')
        self.voicemail.get_old_number_context.return_value = ('1000', 'default')

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
        self.service.edit(self.voicemail)

        self.assertEquals(self.sysconf.move_voicemail.call_count, 0)

    def test_given_number_and_context_have_changed_when_editing_then_sysconfd_called(self):
        self.voicemail.get_old_number_context.return_value = ('1001', 'not_default')

        self.service.edit(self.voicemail)

        self.sysconf.move_voicemail.assert_called_once_with('1001',
                                                            'not_default',
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
