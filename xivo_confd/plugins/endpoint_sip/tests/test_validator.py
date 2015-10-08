# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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
from mock import Mock, sentinel

from xivo_dao.helpers.exception import ResourceError
from xivo_confd.plugins.endpoint_sip.validator import UsernameChanged


class TestUniqueField(unittest.TestCase):

    def setUp(self):
        self.dao_find = Mock()
        self.dao_get = Mock()
        self.validator = UsernameChanged(self.dao_find, self.dao_get)

    def test_given_username_has_not_changed_then_validation_passes(self):
        model = Mock(id=sentinel.id, username=sentinel.username)
        self.dao_get.return_value = model

        self.validator.validate(model)

        self.dao_get.assert_called_once_with(sentinel.id)

    def test_given_username_has_changed_but_is_unique_then_validation_passes(self):
        old_model = Mock(id=sentinel.id, username=sentinel.old_username)
        new_model = Mock(id=sentinel.id, username=sentinel.new_username)

        self.dao_get.return_value = old_model
        self.dao_find.return_value = None

        self.validator.validate(new_model)

        self.dao_get.assert_called_once_with(sentinel.id)
        self.dao_find.assert_called_once_with(sentinel.new_username)

    def test_given_username_has_changed_but_is_(self):
        old_model = Mock(id=sentinel.id, username=sentinel.old_username)
        new_model = Mock(id=sentinel.id, username=sentinel.new_username)
        existing_model = Mock(id=sentinel.existing_id, username=sentinel.new_username)

        self.dao_get.return_value = old_model
        self.dao_find.return_value = existing_model

        self.assertRaises(ResourceError, self.validator.validate, new_model)
