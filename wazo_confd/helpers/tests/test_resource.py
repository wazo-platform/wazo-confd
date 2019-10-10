# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock, sentinel
from hamcrest import assert_that, equal_to

from wazo_confd.helpers.resource import CRUDService


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

        self.dao.search.assert_called_once_with(tenant_uuids=None, **parameters)
        assert_that(result, equal_to(expected_search_result))

        self.dao.search.reset_mock()
        tenant_uuids = [sentinel.tenant_uuid1, sentinel.tenant_uuid2]

        result = self.service.search(parameters, tenant_uuids=tenant_uuids)

        self.dao.search.assert_called_once_with(tenant_uuids=tenant_uuids, **parameters)

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
