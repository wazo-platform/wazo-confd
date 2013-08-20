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

from xivo_dao.data_handler.line.model import LineSIP
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementNotExistsError, InvalidParametersError
from xivo_restapi.helpers.tests.test_resources import TestResources

BASE_URL = "/1.1/lines_sip"


class TestLineSIPActions(TestResources):

    @patch('xivo_restapi.resources.lines.actions_sip.formatter')
    @patch('xivo_dao.data_handler.line.services.find_all_by_protocol')
    def test_list_lines_with_no_lines(self, mock_line_services_find_all_by_protocol, formatter):
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        formatter.list_to_api.return_value = self._serialize_encode(expected_result)
        mock_line_services_find_all_by_protocol.return_value = []

        result = self.app.get(BASE_URL)

        mock_line_services_find_all_by_protocol.assert_called_once_with('sip')
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.lines.actions_sip.formatter')
    @patch('xivo_dao.data_handler.line.services.find_all_by_protocol')
    def test_list_lines_with_two_lines(self, mock_line_services_find_all_by_protocol, formatter):
        line1 = LineSIP(id=1,
                        username='test1')
        line2 = LineSIP(id=2,
                        username='test2')

        expected_status_code = 200
        expected_result = {
            'total': 2,
            'items': [
                {
                    'id': line1.id,
                    'username': line1.username,
                    'links': [{
                        'href': 'http://localhost/1.1/lines_sip/%d' % line1.id,
                        'rel': 'lines_sip'
                    }]
                },
                {
                    'id': line2.id,
                    'username': line2.username,
                    'links': [{
                        'href': 'http://localhost/1.1/lines_sip/%d' % line2.id,
                        'rel': 'lines_sip'
                    }]
                }
            ]
        }

        formatter.list_to_api.return_value = self._serialize_encode(expected_result)
        mock_line_services_find_all_by_protocol.return_value = [line1, line2]

        result = self.app.get(BASE_URL)

        mock_line_services_find_all_by_protocol.assert_called_once_with('sip')
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.line.services.find_all_by_protocol')
    def test_list_lines_error(self, mock_line_services_find_all_by_protocol):
        expected_status_code = 500

        mock_line_services_find_all_by_protocol.side_effect = Exception

        result = self.app.get(BASE_URL)

        mock_line_services_find_all_by_protocol.assert_called_once_with('sip')
        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_restapi.resources.lines.actions_sip.formatter')
    @patch('xivo_dao.data_handler.line.services.get')
    def test_get(self, mock_line_services_get, formatter):
        line = LineSIP(id=1,
                       username='test1')

        expected_status_code = 200
        expected_result = {
            'id': line.id,
            'username': line.username,
            'links': [{
                'href': 'http://localhost/1.1/lines_sip/%d' % line.id,
                'rel': 'lines_sip'
            }]
        }

        formatter.to_api.return_value = self._serialize_encode(expected_result)
        mock_line_services_get.return_value = line

        result = self.app.get("%s/%d" % (BASE_URL, line.id))

        mock_line_services_get.assert_called_with(line.id)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get_error(self, mock_line_services_get):
        expected_status_code = 500

        mock_line_services_get.side_effect = Exception

        result = self.app.get("%s/1" % BASE_URL)

        mock_line_services_get.assert_called_with(1)
        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get_not_found(self, mock_line_services_get):
        expected_status_code = 404

        mock_line_services_get.side_effect = ElementNotExistsError('line')

        result = self.app.get("%s/1" % BASE_URL)

        mock_line_services_get.assert_called_with(1)
        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_restapi.resources.lines.actions_sip.formatter')
    @patch('xivo_dao.data_handler.line.services.create')
    def test_create(self, mock_line_services_create, formatter):
        line = LineSIP(id=1,
                       provisioning_extension=123456,
                       device_slot=2,
                       username='toto',
                       context='default')

        expected_status_code = 201
        expected_result = {
            "id": line.id,
            "links": [{
                "href": "http://localhost/1.1/lines_sip/%d" % line.id,
                "rel": "lines_sip"
            }]
        }

        mock_line_services_create.return_value = line
        formatter.to_api.return_value = self._serialize_encode(expected_result)

        data = {
            'provisioning_extension': line.provisioning_extension,
            'device_slot': line.device_slot,
            'username': line.username,
            'context': line.context
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        formatter.to_model.assert_called_with(data_serialized)
        formatter.to_api.assert_called_with(line)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.lines.actions_sip.formatter')
    @patch('xivo_dao.data_handler.line.services.create')
    def test_create_error(self, mock_line_services_create, formatter):
        expected_status_code = 500

        data = {
            'username': 'toto',
            'context': 'default'
        }
        data_serialized = self._serialize_encode(data)

        mock_line_services_create.side_effect = Exception

        result = self.app.post(BASE_URL, data=data_serialized)

        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_restapi.resources.lines.actions_sip.formatter')
    @patch('xivo_dao.data_handler.line.services.create')
    def test_create_missing_parameters_error(self, mock_line_services_create, formatter):
        expected_status_code = 400
        expected_result = ["Missing parameters: context"]

        mock_line_services_create.side_effect = MissingParametersError(["context"])

        data = {
            'username': 'toto'
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.lines.actions_sip.formatter')
    @patch('xivo_dao.data_handler.line.services.create')
    def test_create_invalid_parameters_error(self, mock_line_services_create, formatter):
        expected_status_code = 400
        expected_result = ["Invalid parameters: context"]

        mock_line_services_create.side_effect = InvalidParametersError(["context"])

        data = {
            'context': ''
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.lines.actions_sip.formatter')
    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.edit')
    def test_edit(self, mock_line_services_edit, mock_line_services_get, formatter):
        line = LineSIP(id=223,
                       username='tata',
                       context='default')
        expected_status_code = 204
        expected_result = ''

        data = {
            'username': 'toto'
        }
        data_serialized = self._serialize_encode(data)
        line_edited = line

        mock_line_services_get.return_value = line

        result = self.app.put("%s/%d" % (BASE_URL, line.id), data=data_serialized)

        formatter.to_model_update.assert_called_with(data_serialized, line)
        mock_line_services_get.assert_called_once_with(line.id)
        line_edited.username = data['username']
        mock_line_services_edit.assert_called_once_with(line_edited)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_result))

    @patch('xivo_restapi.resources.lines.actions_sip.formatter')
    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.edit')
    def test_edit_error(self, mock_line_services_edit, mock_line_services_get, formatter):
        expected_status_code = 500

        data = {
            'username': 'toto'
        }
        data_serialized = self._serialize_encode(data)

        mock_line_services_get.return_value = line = Mock(LineSIP)
        mock_line_services_edit.side_effect = Exception

        result = self.app.put("%s/1" % BASE_URL, data=data_serialized)

        formatter.to_model_update.assert_called_with(data_serialized, line)
        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_restapi.resources.lines.actions_sip.formatter')
    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.edit')
    def test_edit_not_found(self, mock_line_services_edit, mock_line_services_get, formatter):
        expected_status_code = 404

        data = {
            'username': 'toto'
        }
        data_serialized = self._serialize_encode(data)

        mock_line_services_get.return_value = Mock(LineSIP)
        mock_line_services_edit.side_effect = ElementNotExistsError('line')

        result = self.app.put("%s/1" % BASE_URL, data=data_serialized)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(formatter.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.delete')
    def test_delete_success(self, mock_line_services_delete, mock_line_services_get):
        expected_status_code = 204
        expected_result = ''

        line = Mock(LineSIP)
        mock_line_services_get.return_value = line
        mock_line_services_delete.return_value = True

        result = self.app.delete("%s/1" % BASE_URL)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_result))
        mock_line_services_delete.assert_called_with(line)

    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.delete')
    def test_delete_not_found(self, mock_line_services_delete, mock_line_services_get):
        expected_status_code = 404

        line = Mock(LineSIP)
        mock_line_services_get.return_value = line
        mock_line_services_delete.side_effect = ElementNotExistsError('line')

        result = self.app.delete("%s/1" % BASE_URL)

        assert_that(result.status_code, equal_to(expected_status_code))
        mock_line_services_delete.assert_called_with(line)
