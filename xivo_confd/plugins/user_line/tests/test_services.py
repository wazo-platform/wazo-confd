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

from mock import Mock, sentinel
from hamcrest import assert_that, equal_to

from xivo_dao.tests.test_case import TestCase

from xivo_confd.plugins.user_line import service as user_line_services


class TestUserLineService(TestCase):

    def setUp(self):
        self.dao = Mock()
        self.user_dao = Mock()
        self.line_dao = Mock()
        self.validator = Mock()
        self.notifier = Mock()
        self.service = user_line_services.UserLineService(self.dao,
                                                          self.user_dao,
                                                          self.line_dao,
                                                          self.validator,
                                                          self.notifier)

    def test_when_validating_parent_then_user_dao_called(self):
        association = Mock()

        self.service.validate_parent(association)

        self.user_dao.get.assert_called_once_with(association)

    def test_when_validating_resource_then_user_dao_called(self):
        association = Mock()

        self.service.validate_resource(association)

        self.line_dao.get.assert_called_once_with(association)

    def test_when_listing_associations_then_dao_is_called(self):
        expected_user_lines = self.dao.find_all_by_user_id.return_value

        result = self.service.list(sentinel.user_id)

        self.dao.find_all_by_user_id.assert_called_once_with(sentinel.user_id)
        assert_that(result, equal_to(expected_user_lines))

    def test_when_listing_associations_by_line_then_dao_is_called(self):
        expected_user_lines = self.dao.find_all_by_line_id.return_value

        result = self.service.list_by_line(sentinel.line_id)

        self.dao.find_all_by_line_id.assert_called_once_with(sentinel.line_id)
        assert_that(result, equal_to(expected_user_lines))

    def test_when_getting_association_then_dao_is_called(self):
        expected_user_line = self.dao.get_by_user_id_and_line_id.return_value

        result = self.service.get(sentinel.user_id, sentinel.line_id)

        self.dao.get_by_user_id_and_line_id.assert_called_once_with(sentinel.user_id,
                                                                    sentinel.line_id)
        assert_that(result, equal_to(expected_user_line))

    def test_when_associating_then_validator_is_called(self):
        association = Mock()
        self.service.associate(association)

        self.validator.validate_association.assert_called_once_with(association)

    def test_when_associating_then_dao_is_called(self):
        association = Mock()
        result = self.service.associate(association)

        self.dao.associate.assert_called_once_with(association)
        assert_that(result, equal_to(self.dao.associate.return_value))

    def test_when_associating_then_notifier_is_called(self):
        association = Mock()
        self.service.associate(association)

        self.notifier.associated.assert_called_once_with(self.dao.associate.return_value)

    def test_when_dissociating_then_validator_is_called(self):
        dissociation = Mock()
        self.service.dissociate(dissociation)

        self.validator.validate_dissociation.assert_called_once_with(dissociation)

    def test_when_dissociating_then_dao_is_called(self):
        dissociation = Mock()
        self.service.dissociate(dissociation)

        self.dao.dissociate.assert_called_once_with(dissociation)

    def test_when_dissociating_then_notifier_is_called(self):
        dissociation = Mock()
        self.service.dissociate(dissociation)

        self.notifier.dissociated.assert_called_once_with(dissociation)
