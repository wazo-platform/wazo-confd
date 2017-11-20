# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, sentinel, patch
from hamcrest import assert_that, equal_to

from xivo_confd.plugins.func_key.service import TemplateService
from xivo_confd.plugins.device.update import DeviceUpdater
from xivo_dao.resources.func_key_template.model import FuncKeyTemplate
from xivo_dao.alchemy.userfeatures import UserFeatures as User


class TestTemplateService(unittest.TestCase):

    def setUp(self):
        self.validator = Mock()
        self.validator_bsfilter = Mock()
        self.template_dao = Mock()

        self.user_dao = Mock()
        self.user_dao.find_all_by.return_value = []

        self.notifier = Mock()
        self.device_updater = Mock(DeviceUpdater)

        self.template = FuncKeyTemplate(id=sentinel.template_id, name=sentinel.name)
        self.service = TemplateService(self.template_dao,
                                       self.user_dao,
                                       self.validator,
                                       self.validator_bsfilter,
                                       self.notifier,
                                       self.device_updater)

    def test_when_searching_then_returns_search_from_database(self):
        expected_search = self.template_dao.search.return_value

        result = self.service.search({'search': 'search'})

        assert_that(expected_search, equal_to(result))
        self.template_dao.search.assert_called_once_with(search='search')

    def test_when_getting_then_returns_template_from_database(self):
        expected_template = self.template_dao.get.return_value

        result = self.service.get(sentinel.template_id)

        assert_that(expected_template, equal_to(result))
        self.template_dao.get.assert_called_once_with(sentinel.template_id)

    def test_when_creating_then_validates_template(self):
        self.service.create(self.template)

        self.validator.validate_create.assert_called_once_with(self.template)

    def test_when_creating_then_creates_template_in_database(self):
        created_template = self.template_dao.create.return_value

        result = self.service.create(self.template)

        assert_that(result, equal_to(created_template))
        self.template_dao.create.assert_called_once_with(self.template)

    def test_when_creating_then_sends_notification(self):
        created_template = self.template_dao.create.return_value

        self.service.create(self.template)

        self.notifier.created.assert_called_once_with(created_template)

    def test_when_editing_then_validates_template(self):
        self.service.edit(self.template)

        self.validator.validate_edit.assert_called_once_with(self.template)

    def test_when_editing_then_updates_template_in_database(self):
        self.service.edit(self.template)

        self.template_dao.edit.assert_called_once_with(self.template)

    def test_when_editing_then_sends_notification(self):
        self.service.edit(self.template, None)

        self.notifier.edited.assert_called_once_with(self.template, None)

    def test_when_editing_then_updates_func_keys_for_device(self):
        self.service.edit(self.template)

        self.device_updater.update_for_template.assert_called_once_with(self.template)

    def test_when_deleting_then_validates_template(self):
        self.service.delete(self.template)

        self.validator.validate_delete.assert_called_once_with(self.template)

    @patch('xivo_dao.helpers.db_manager.Session.expire')
    def test_when_deleting_then_updates_devices_associated_to_users(self, session_expire):
        expected_user = User(func_key_template_id=sentinel.func_key_template_id)
        self.user_dao.find_all_by.return_value = [expected_user]

        self.service.delete(self.template)

        self.device_updater.update_for_user.assert_called_once_with(expected_user)
        self.user_dao.find_all_by.assert_called_once_with(func_key_template_id=self.template.id)

    def test_when_deleting_then_deletes_template_in_database(self):
        self.service.delete(self.template)

        self.template_dao.delete.assert_called_once_with(self.template)

    def test_when_deleting_then_sends_notification(self):
        self.service.delete(self.template)

        self.notifier.deleted.assert_called_once_with(self.template)
