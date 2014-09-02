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

import unittest
from hamcrest import equal_to, assert_that
from xivo_dao.data_handler.user_voicemail.model import UserVoicemail
from xivo_confd.resources.user_voicemail.formatter import UserVoicemailFormatter


class TestUserVoicemailFormatter(unittest.TestCase):

    def test_dict_to_model(self):
        user_id = 1
        voicemail_id = 2
        data = {'voicemail_id': voicemail_id}

        expected = UserVoicemail(user_id=user_id, voicemail_id=voicemail_id)

        formatter = UserVoicemailFormatter()
        result = formatter.dict_to_model(data, user_id)

        assert_that(result, equal_to(expected))
