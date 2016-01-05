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
from hamcrest import assert_that, calling, raises

from mock import Mock
from xivo_dao.helpers.exception import ResourceError
from xivo_dao.resources.user_voicemail.model import UserVoicemail

from xivo_confd.plugins.user_voicemail.validator import UserHasNoVoicemail


class TestUserHasNoVoicemail(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = UserHasNoVoicemail(self.dao)

    def test_given_user_has_no_voicemail_then_validation_passes(self):
        model = UserVoicemail(user_id=1, voicemail_id=2)
        self.dao.find_by_user_id.return_value = None

        self.validator.validate(model)

    def test_given_user_has_a_voicemail_then_validation_passes(self):
        model = UserVoicemail(user_id=1, voicemail_id=2)
        self.dao.find_by_user_id.return_value = model

        assert_that(
            calling(self.validator.validate).with_args(model),
            raises(ResourceError))
