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
from mock import Mock, sentinel
from hamcrest import assert_that, equal_to

from xivo_confd.plugins.line_extension.proxy import LineExtensionProxyService


class TestLineExtensionService(unittest.TestCase):

    def setUp(self):
        self.old_service = Mock()
        self.line_dao = Mock()
        self.extension_dao = Mock()
        self.service = LineExtensionProxyService(self.old_service, self.line_dao, self.extension_dao)

    def test_when_listing_associations_then_service_is_called(self):
        expected_line_extensions = self.old_service.get_all_by_line_id.return_value

        result = self.service.list(sentinel.line_id)

        self.old_service.get_all_by_line_id.assert_called_once_with(sentinel.line_id)
        assert_that(result, equal_to(expected_line_extensions))

    def test_when_getting_association_then_model_built(self):
        result = self.service.get(sentinel.line_id, sentinel.extension_id)

        assert_that(result.line_id, equal_to(sentinel.line_id))
        assert_that(result.extension_id, equal_to(sentinel.extension_id))

    def test_when_associating_then_service_is_called(self):
        association = Mock()

        self.service.associate(association)

        self.old_service.associate.assert_called_once_with(association)

    def test_when_dissociating_then_service_is_called(self):
        association = Mock()

        self.service.dissociate(association)

        self.old_service.dissociate.assert_called_once_with(association)

    def test_when_getting_parent_then_service_is_called(self):
        expected_line_voicemail = self.old_service.get_by_line_id.return_value

        result = self.service.get_by_parent(sentinel.line_id)

        self.old_service.get_by_line_id.assert_called_once_with(sentinel.line_id)
        assert_that(result, equal_to(expected_line_voicemail))

    def test_when_getting_extension_then_service_is_called(self):
        expected_line_extension = self.old_service.get_by_extension_id.return_value

        result = self.service.get_by_extension_id(sentinel.extension_id)

        self.old_service.get_by_extension_id.assert_called_once_with(sentinel.extension_id)
        assert_that(result, equal_to(expected_line_extension))
