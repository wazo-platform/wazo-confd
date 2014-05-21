# -*- coding: UTF-8 -*-

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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

from mock import patch

from xivo_dao.data_handler.extension.model import Extension, ExtensionOrdering
from xivo_dao.helpers.abstract_model import SearchResult
from xivo_restapi.helpers.tests.test_resources import TestResources

BASE_URL = "/1.1/extensions"


class TestExtensionActions(TestResources):

    def setUp(self):
        super(TestResources, self).setUp()
        self.extension = Extension(id=1, exten='1234', context='default')

    def build_item(self, extension):
        links = [{'href': 'http://localhost/1.1/extensions/%d' % extension.id,
                  'rel': 'extensions'}]

        item = {'id': extension.id,
                'exten': extension.exten,
                'context': extension.context,
                'commented': extension.commented,
                'links': links}

        return item

    @patch('xivo_dao.data_handler.extension.services.search')
    def test_list_extensions_with_no_extensions(self, mock_extension_services_search):
        expected_response = {'total': 0,
                             'items': []}

        mock_extension_services_search.return_value = SearchResult(0, [])

        response = self.app.get(BASE_URL)

        mock_extension_services_search.assert_any_call()
        self.assert_response_for_get(response, expected_response)

    @patch('xivo_dao.data_handler.extension.services.search')
    def test_list_extensions_with_two_extensions(self, mock_extension_services_search):
        extension1 = Extension(id=1, exten='1324', context='default')
        extension2 = Extension(id=2, exten='1325', context='default')

        expected_response = {'total': 2,
                             'items': [self.build_item(extension1),
                                       self.build_item(extension2)]}

        mock_extension_services_search.return_value = SearchResult(2, [extension1, extension2])

        response = self.app.get(BASE_URL)

        mock_extension_services_search.assert_any_call()
        self.assert_response_for_get(response, expected_response)

    @patch('xivo_dao.data_handler.extension.services.search')
    def test_list_extensions_with_search(self, extension_search):
        expected_response = {'total': 1,
                             'items': [self.build_item(self.extension)]}

        extension_search.return_value = SearchResult(1, [self.extension])

        query_string = "search=toto&order=exten&direction=desc&skip=1&limit=2"
        response = self.app.get("%s?%s" % (BASE_URL, query_string))

        extension_search.assert_called_once_with(search='toto',
                                                 order=ExtensionOrdering.exten,
                                                 direction='desc',
                                                 skip=1,
                                                 limit=2)
        self.assert_response_for_get(response, expected_response)

    @patch('xivo_dao.data_handler.extension.services.get')
    def test_get(self, mock_extension_services_get):
        expected_response = self.build_item(self.extension)

        mock_extension_services_get.return_value = self.extension

        response = self.app.get("%s/%d" % (BASE_URL, self.extension.id))

        mock_extension_services_get.assert_called_with(self.extension.id)
        self.assert_response_for_get(response, expected_response)

    @patch('xivo_dao.data_handler.extension.services.create')
    def test_create(self, mock_extension_services_create):
        expected_response = self.build_item(self.extension)

        mock_extension_services_create.return_value = self.extension

        data = {u'exten': u'1324', u'context': u'default'}
        data_serialized = self._serialize_encode(data)
        response = self.app.post(BASE_URL, data=data_serialized)

        self.assert_response_for_create(response, expected_response)

    @patch('xivo_dao.data_handler.extension.services.get')
    @patch('xivo_dao.data_handler.extension.services.edit')
    def test_edit(self, mock_extension_services_edit, mock_extension_services_get):
        mock_extension_services_get.return_value = self.extension

        data = {'exten': '1324', 'context': 'default'}
        data_serialized = self._serialize_encode(data)
        response = self.app.put("%s/%d" % (BASE_URL, self.extension.id), data=data_serialized)

        self.assert_response_for_update(response)
        mock_extension_services_edit.assert_called_once_with(self.extension)

    @patch('xivo_dao.data_handler.extension.services.get')
    @patch('xivo_dao.data_handler.extension.services.delete')
    def test_delete_success(self, mock_extension_services_delete, mock_extension_services_get):
        mock_extension_services_get.return_value = self.extension

        response = self.app.delete("%s/%d" % (BASE_URL, self.extension.id))

        self.assert_response_for_delete(response)
        mock_extension_services_delete.assert_called_with(self.extension)
