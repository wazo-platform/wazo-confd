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

from hamcrest import assert_that, equal_to

from xivo_restapi.helpers.tests.test_resources import TestResources

from mock import patch


LINE_ID = 1
EXTENSION_ID = 2

BASE_URL = "/1.1/lines/%d/extensions"
DELETE_URL = BASE_URL + "/%d"


class TestLineExtensionCollectionRoutes(TestResources):

    @patch('xivo_restapi.resources.line_extension_collection.actions.list_extensions')
    def test_list_extensions(self, list_extensions):
        status = 200
        expected_response = {'total': 1,
                             'items': [{
                                 'line_id': LINE_ID,
                                 'extension_id': EXTENSION_ID,
                                 'links': [
                                     {'href': 'http://localhost/1.1/lines/%d' % LINE_ID,
                                      'rel': 'lines'},
                                     {'href': 'http://localhost/1.1/extensions/%d' % EXTENSION_ID,
                                      'rel': 'extensions'},
                                 ]
                             }]
                             }
        list_extensions.return_value = self._serialize_encode(expected_response)

        response = self.app.get(BASE_URL % LINE_ID)

        list_extensions.assert_called_once_with(LINE_ID)
        self.assert_response(response, status, expected_response)

    @patch('xivo_restapi.resources.line_extension_collection.actions.associate_extension')
    def test_associate_extension(self, associate_extension):
        parameters = self._serialize_encode({'extension_id': EXTENSION_ID})

        status = 201
        expected_response = {'line_id': LINE_ID,
                             'extension_id': EXTENSION_ID,
                             'links': [
                                 {'href': 'http://localhost/1.1/lines/%d' % LINE_ID,
                                  'rel': 'lines'},
                                 {'href': 'http://localhost/1.1/extensions/%d' % EXTENSION_ID,
                                  'rel': 'extensions'}
                             ]}
        associate_extension.return_value = self._serialize_encode(expected_response)

        response = self.app.post(BASE_URL % LINE_ID, data=parameters)

        associate_extension.assert_called_once_with(LINE_ID, parameters)
        self.assert_response(response, status, expected_response)

    @patch('xivo_restapi.resources.line_extension_collection.actions.dissociate_extension')
    def test_dissociate_extension(self, dissociate_extension):
        status = 204
        expected_response = dissociate_extension.return_value = ''

        response = self.app.delete(DELETE_URL % (LINE_ID, EXTENSION_ID))

        dissociate_extension.assert_called_once_with(LINE_ID, EXTENSION_ID)
        assert_that(response.status_code, equal_to(status))
        assert_that(response.data, equal_to(expected_response))
