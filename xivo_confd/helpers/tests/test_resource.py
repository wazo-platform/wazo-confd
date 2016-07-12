# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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

from xivo_confd.helpers.resource import CRUDService


class TestCRUDService(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = Mock()
        self.notifier = Mock()
        self.service = CRUDService(self.dao, self.validator, self.notifier)

    def test_when_searching_then_dao_is_searched(self):
        parameters = {'param': 'value'}
        expected_search_result = self.dao.search.return_value

        result = self.service.search(parameters)

        self.dao.search.assert_called_once_with(**parameters)
        assert_that(result, equal_to(expected_search_result))

    def test_when_getting_then_resource_is_fetched_from_dao(self):
        expected_resource = self.dao.get.return_value

        result = self.service.get(sentinel.resource_id)

        self.dao.get.assert_called_once_with(sentinel.resource_id)
        assert_that(result, equal_to(expected_resource))

    def test_when_creating_then_resource_validated(self):
        self.service.create(sentinel.resource)

        self.validator.validate_create.assert_called_once_with(sentinel.resource)

    def test_when_creating_then_resource_created_with_dao(self):
        expected_resource = self.dao.create.return_value

        result = self.service.create(sentinel.resource)

        self.dao.create.assert_called_with(sentinel.resource)
        assert_that(result, equal_to(expected_resource))

    def test_when_creating_then_notifier_is_notified_using_resource(self):
        expected_resource = self.dao.create.return_value

        self.service.create(sentinel.resource)

        self.notifier.created.assert_called_once_with(expected_resource)

    def test_when_editing_then_resource_validated(self):
        self.service.edit(sentinel.resource)

        self.validator.validate_edit.assert_called_once_with(sentinel.resource)

    def test_when_editing_then_resource_edited_with_dao(self):
        self.service.edit(sentinel.resource)

        self.dao.edit.assert_called_with(sentinel.resource)

    def test_when_editing_then_notifier_is_notified_using_resource(self):
        self.service.edit(sentinel.resource)

        self.notifier.edited.assert_called_once_with(sentinel.resource)

    def test_when_deleting_then_resource_validated(self):
        self.service.delete(sentinel.resource)

        self.validator.validate_delete.assert_called_once_with(sentinel.resource)

    def test_when_deleting_then_resource_edited_with_dao(self):
        self.service.delete(sentinel.resource)

        self.dao.delete.assert_called_with(sentinel.resource)

    def test_when_deleting_then_notifier_is_notified_using_resource(self):
        self.service.delete(sentinel.resource)

        self.notifier.deleted.assert_called_once_with(sentinel.resource)
