# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from mock import patch

from xivo_restapi.helpers.tests.test_resources import TestResources
from xivo_dao.data_handler.line_extension.model import LineExtension


LINE_ID = 1
EXTENSION_ID = 2

BASE_URL = "/1.1/lines/%d/extensions"
DELETE_URL = BASE_URL + "/%d"


@patch('xivo_restapi.helpers.url.check_line_exists')
class TestLineExtensionCollectionRoutes(TestResources):

    def build_item(self, line_extension):
        return {'line_id': line_extension.line_id,
                'extension_id': line_extension.extension_id,
                'links': [
                    {'rel': 'lines',
                     'href': 'http://localhost/1.1/lines/%d' % line_extension.line_id},
                    {'rel': 'extensions',
                     'href': 'http://localhost/1.1/extensions/%d' % line_extension.extension_id}
                ]}

    @patch('xivo_dao.data_handler.line_extension.services.get_all_by_line_id')
    def test_list_extensions(self, get_all_by_line_id, line_exists):
        line_extension = LineExtension(line_id=LINE_ID, extension_id=EXTENSION_ID)
        get_all_by_line_id.return_value = [line_extension]

        expected = {'total': 1,
                    'items': [self.build_item(line_extension)]}

        response = self.app.get(BASE_URL % LINE_ID)

        self.assert_response_for_get(response, expected)
        line_exists.assert_called_once_with(LINE_ID)
        get_all_by_line_id.assert_called_once_with(LINE_ID)

    @patch('xivo_dao.data_handler.line_extension.services.associate')
    def test_associate_extension(self, associate, line_exists):
        line_extension = LineExtension(line_id=LINE_ID, extension_id=EXTENSION_ID)
        associate.return_value = line_extension

        expected = self.build_item(line_extension)

        parameters = {'extension_id': EXTENSION_ID}
        response = self.app.post(BASE_URL % LINE_ID, data=self._serialize_encode(parameters))

        self.assert_response_for_create(response, expected)
        line_exists.assert_called_once_with(LINE_ID)
        associate.assert_called_once_with(line_extension)

    @patch('xivo_dao.data_handler.line_extension.services.dissociate')
    def test_dissociate_extension(self, dissociate, line_exists):
        line_extension = LineExtension(line_id=LINE_ID, extension_id=EXTENSION_ID)

        response = self.app.delete(DELETE_URL % (LINE_ID, EXTENSION_ID))

        self.assert_response_for_delete(response)
        line_exists.assert_called_once_with(LINE_ID)
        dissociate.assert_called_once_with(line_extension)
