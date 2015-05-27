# -*- coding: UTF-8 -*-

# Copyright (C) 2013-2015 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..


import unittest

from mock import patch, Mock, sentinel
from hamcrest import assert_that, equal_to

from xivo_confd.resources.func_keys.service import TemplateService, DeviceUpdater
from xivo_confd.resources.func_keys.model import FuncKeyTemplate


class TestTemplateService(unittest.TestCase):

    def setUp(self):
        self.validator = Mock()
        self.template_dao = Mock()
        self.user_dao = Mock()
        self.notifier = Mock()
        self.device_updater = Mock(DeviceUpdater)

        self.template = FuncKeyTemplate(id=sentinel.template_id, name=sentinel.name)
        self.service = TemplateService(self.validator,
                                       self.template_dao,
                                       self.user_dao,
                                       self.notifier,
                                       self.device_updater)


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
        self.service.edit(self.template)

        self.notifier.edited.assert_called_once_with(self.template)

    def test_when_editing_then_updates_func_keys_for_device(self):
        self.service.edit(self.template)

        self.device_updater.update_for_template.assert_called_once_with(self.template)

    def test_when_deleting_then_validates_template(self):
        self.service.delete(self.template)

        self.validator.validate_delete.assert_called_once_with(self.template)

    def test_when_deleting_then_updates_devices_associated_to_users(self):
        expected_users = self.user_dao.find_all_by_template_id.return_value

        self.service.delete(self.template)

        self.device_updater.update_for_users.assert_called_once_with(expected_users)
        self.user_dao.find_all_by_template_id.assert_called_once_with(self.template.id)

    def test_when_deleting_then_deletes_template_in_database(self):
        self.service.delete(self.template)

        self.template_dao.delete.assert_called_once_with(self.template)

    def test_when_deleting_then_sends_notification(self):
        self.service.delete(self.template)

        self.notifier.deleted.assert_called_once_with(self.template)
