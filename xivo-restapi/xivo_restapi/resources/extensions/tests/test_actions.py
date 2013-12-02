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

from mock import Mock, patch
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.extension.model import Extension
from xivo_restapi.helpers.tests.test_resources import TestResources
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension

BASE_URL = "/1.1/extensions"


class TestExtensionActions(TestResources):

    @patch('xivo_dao.data_handler.extension.services.find_all')
    def test_list_extensions_with_no_extensions(self, mock_extension_services_find_all):
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_extension_services_find_all.return_value = []

        result = self.app.get(BASE_URL)

        mock_extension_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.extension.services.find_all')
    def test_list_extensions_with_two_extensions(self, mock_extension_services_find_all):
        extension_id_1 = 42
        extension_id_2 = 22
        expected_status_code = 200
        expected_result = {
            'total': 2,
            'items': [
                {
                    'id': extension_id_1,
                    'exten': '1324',
                    'context': 'default',
                    'commented': False,
                    'links': [{
                        'href': 'http://localhost/1.1/extensions/%d' % extension_id_1,
                        'rel': 'extensions'
                    }]
                },
                {
                    'id': extension_id_2,
                    'exten': '1325',
                    'context': 'default',
                    'commented': False,
                    'links': [{
                        'href': 'http://localhost/1.1/extensions/%d' % extension_id_2,
                        'rel': 'extensions'
                    }]
                }
            ]
        }

        extension1 = Extension(id=extension_id_1,
                               exten='1324',
                               context='default')
        extension2 = Extension(id=extension_id_2,
                               exten='1325',
                               context='default')
        mock_extension_services_find_all.return_value = [extension1, extension2]

        result = self.app.get(BASE_URL)

        mock_extension_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.extension.services.find_by_exten')
    def test_list_extensions_with_search(self, mock_extension_services_find_by_exten):
        extension_id = 9987
        search = 'bob'
        expected_status_code = 200

        expected_result = {
            'total': 1,
            'items': [
                {
                    'id': extension_id,
                    'exten': '1324',
                    'context': 'default',
                    'commented': False,
                    'links': [{
                        'href': 'http://localhost/1.1/extensions/%d' % extension_id,
                        'rel': 'extensions'
                    }]
                }
            ]
        }

        extension = Extension(id=extension_id,
                              exten='1324',
                              context='default')
        mock_extension_services_find_by_exten.return_value = [extension]

        result = self.app.get("%s?q=%s" % (BASE_URL, search))

        mock_extension_services_find_by_exten.assert_called_once_with(search)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_extension_id')
    def test_list_user_links_not_found(self, mock_ule_services_find_all_by_extension_id):
        extension_id = 1370
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_ule_services_find_all_by_extension_id.return_value = []

        result = self.app.get("%s/%d/user_links" % (BASE_URL, extension_id))

        mock_ule_services_find_all_by_extension_id.assert_called_once_with(extension_id)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_extension_id')
    def test_list_user_links(self, mock_ule_services_find_all_by_extension_id):
        expected_status_code = 200
        user_link_id = 83
        user_id = 14
        line_id = 42324
        extension_id = 2132

        expected_result = {
            "total": 1,
            "items": [
                {
                    "id": user_link_id,
                    "user_id": user_id,
                    "line_id": line_id,
                    "extension_id": extension_id,
                    "main_user": True,
                    "main_line": True,
                    "links": [
                        {
                            "rel": "user_links",
                            "href": "http://localhost/1.1/user_links/%d" % user_link_id
                        },
                        {
                            "rel": "users",
                            "href": "http://localhost/1.1/users/%d" % user_id
                        },
                        {
                            "rel": "lines",
                            "href": "http://localhost/1.1/lines/%d" % line_id
                        },
                        {
                            "rel": "extensions",
                            "href": "http://localhost/1.1/extensions/%d" % extension_id
                        }
                    ]
                }
            ]
        }

        mock_ule_services_find_all_by_extension_id.return_value = [
            UserLineExtension(id=user_link_id,
                              user_id=user_id,
                              line_id=line_id,
                              extension_id=extension_id,
                              main_user=True,
                              main_line=True)
        ]

        result = self.app.get("%s/%d/user_links" % (BASE_URL, extension_id))

        mock_ule_services_find_all_by_extension_id.assert_called_once_with(extension_id)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.extension.services.get')
    def test_get(self, mock_extension_services_get):
        extension_id = 1
        expected_status_code = 200
        expected_result = {
            'id': extension_id,
            'exten': '1324',
            'commented': False,
            'context': 'default',
            'links': [{
                'href': 'http://localhost/1.1/extensions/%d' % extension_id,
                'rel': 'extensions'
            }]
        }

        extension = Extension(id=extension_id,
                              exten='1324',
                              context='default')

        mock_extension_services_get.return_value = extension

        result = self.app.get("%s/%d" % (BASE_URL, extension_id))

        mock_extension_services_get.assert_called_with(extension_id)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.extensions.actions.formatter')
    @patch('xivo_dao.data_handler.extension.services.create')
    def test_create(self, mock_extension_services_create, formatter):
        extension_id = 1
        expected_status_code = 201
        expected_result = {
            'id': extension_id,
            'links': [
                {
                    'rel': 'extensions',
                    'href': 'http://localhost/1.1/extensions/%d' % extension_id,
                }
            ]
        }

        extension = Mock(Extension)
        extension.id = extension_id

        mock_extension_services_create.return_value = extension
        formatter.to_api.return_value = self._serialize_encode(expected_result)

        data = {
            u'exten': u'1324',
            u'context': u'jd'
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        formatter.to_model.assert_called_with(data_serialized)
        formatter.to_api.assert_called_with(extension)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.extensions.actions.formatter')
    @patch('xivo_dao.data_handler.extension.services.get')
    @patch('xivo_dao.data_handler.extension.services.edit')
    def test_edit(self, mock_extension_services_edit, mock_extension_services_get, formatter):
        expected_status_code = 204
        expected_data = ''

        data = {
            'exten': '1324',
            'context': 'jd'
        }
        data_serialized = self._serialize_encode(data)

        mock_extension_services_get.return_value = extension = Mock(Extension)

        result = self.app.put("%s/1" % BASE_URL, data=data_serialized)

        formatter.update_model.assert_called_with(data_serialized, extension)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_data))

    @patch('xivo_dao.data_handler.extension.services.get')
    @patch('xivo_dao.data_handler.extension.services.delete')
    def test_delete_success(self, mock_extension_services_delete, mock_extension_services_get):
        expected_status_code = 204
        expected_data = ''

        extension = Mock(Extension)
        mock_extension_services_get.return_value = extension
        mock_extension_services_delete.return_value = True

        result = self.app.delete("%s/1" % BASE_URL)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_data))
        mock_extension_services_delete.assert_called_with(extension)
