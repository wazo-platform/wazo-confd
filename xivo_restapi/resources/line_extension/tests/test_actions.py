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

from mock import patch
from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_restapi.helpers.tests.test_resources import TestResources


LINE_URL = "/1.1/lines/%s/extension"
EXTENSION_URL = "/1.1/extensions/%s/line"


class TestLineExtensionActions(TestResources):

    def setUp(self):
        super(TestLineExtensionActions, self).setUp()
        self.line_extension = LineExtension(line_id=1,
                                            extension_id=2)

    def build_item(self, line_extension):
        line_link = {"rel": "lines",
                     "href": "http://localhost/1.1/lines/%s" % line_extension.line_id}

        extension_link = {"rel": "extensions",
                          "href": "http://localhost/1.1/extensions/%s" % line_extension.extension_id}

        return {'line_id': line_extension.line_id,
                'extension_id': line_extension.extension_id,
                'links': [line_link, extension_link]}

    @patch('xivo_restapi.helpers.url.check_line_exists')
    @patch('xivo_dao.data_handler.line_extension.services.associate')
    def test_associate_extension(self, line_extension_associate, line_exists):
        line_extension_associate.return_value = self.line_extension

        expected_result = self.build_item(self.line_extension)

        data = {'extension_id': self.line_extension.extension_id}

        result = self.app.post(LINE_URL % self.line_extension.line_id,
                               data=self._serialize_encode(data))

        self.assert_response_for_create(result, expected_result)
        line_exists.assert_called_once_with(self.line_extension.line_id)
        line_extension_associate.assert_called_once_with(self.line_extension)

    @patch('xivo_restapi.helpers.url.check_line_exists')
    @patch('xivo_dao.data_handler.line_extension.services.get_by_line_id')
    def test_get_extension_associated_to_a_line(self, line_extension_get_by_line_id, line_exists):
        line_extension_get_by_line_id.return_value = self.line_extension

        expected_result = self.build_item(self.line_extension)

        result = self.app.get(LINE_URL % self.line_extension.line_id)

        self.assert_response_for_get(result, expected_result)
        line_exists.assert_called_once_with(self.line_extension.line_id)
        line_extension_get_by_line_id.assert_called_once_with(self.line_extension.line_id)

    @patch('xivo_restapi.helpers.url.check_extension_exists')
    @patch('xivo_dao.data_handler.line_extension.services.get_by_extension_id')
    def test_get_line_associated_to_an_extension(self, line_extension_get_by_extension_id, extension_exists):
        line_extension_get_by_extension_id.return_value = self.line_extension

        expected_result = self.build_item(self.line_extension)

        result = self.app.get(EXTENSION_URL % self.line_extension.extension_id)

        self.assert_response_for_get(result, expected_result)
        extension_exists.assert_called_once_with(self.line_extension.extension_id)
        line_extension_get_by_extension_id.assert_called_once_with(self.line_extension.extension_id)

    @patch('xivo_restapi.helpers.url.check_line_exists')
    @patch('xivo_dao.data_handler.line_extension.services.get_by_line_id')
    @patch('xivo_dao.data_handler.line_extension.services.dissociate')
    def test_dissociate_extension(self, line_extension_dissociate, get_by_line_id, line_exists):
        get_by_line_id.return_value = self.line_extension

        result = self.app.delete(LINE_URL % self.line_extension.line_id)

        self.assert_response_for_delete(result)
        line_exists.assert_called_once_with(self.line_extension.line_id)
        get_by_line_id.assert_called_once_with(self.line_extension.line_id)
        line_extension_dissociate.assert_called_once_with(self.line_extension)
