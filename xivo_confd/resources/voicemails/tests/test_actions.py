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

from xivo_confd.resources.voicemails.actions import VoicemailService


class TestVoicemailService(unittest.TestCase):

    def setUp(self):
        self.connector = Mock()
        self.service = VoicemailService(Mock(), Mock(), Mock(), self.connector)

    def test_when_deleting_a_voicemail_then_voicemail_storage_deleted(self):
        voicemail = Mock(number='1000', context='default')

        self.service.delete(voicemail)

        self.connector.delete_voicemail_storage.assert_called_once_with(voicemail.number,
                                                                        voicemail.context)
