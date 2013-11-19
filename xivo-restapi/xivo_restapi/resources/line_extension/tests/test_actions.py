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
from hamcrest import assert_that, equal_to, has_entries, contains_inanyorder

from mock import patch
from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_dao.data_handler.line_extension.exception import LineExtensionNotExistsError
from xivo_restapi.helpers.tests.test_resources import TestResources


BASE_URL = "/1.1/lines/%s/extension"


class TestLineExtensionActions(TestResources):

    @patch('xivo_restapi.resources.line_extension.actions.formatter')
    @patch('xivo_dao.data_handler.line_extension.services.associate')
    def test_associate_extension(self, line_extension_associate, formatter):
        line_id = 1
        extension_id = 2

        expected_status_code = 201
        expected_result = {
            'line_id': line_id,
            'extension_id': extension_id,
            'links': [
                {
                    "rel": "lines_sip",
                    "href": "http://localhost/1.1/lines_sip/%s" % line_id,
                },
                {
                    "rel": "extension",
                    "href": "http://localhost/1.1/extensions/%s" % extension_id,
                }
            ]
        }

        line_extension = LineExtension(line_id=line_id, extension_id=extension_id)
        line_extension_associate.return_value = line_extension

        formatter.to_model.return_value = line_extension
        formatter.to_api.return_value = self._serialize_encode(expected_result)

        data = {
            'extension_id': extension_id
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL % line_id, data=data_serialized)

        formatter.to_model.assert_called_once_with(data_serialized, line_id)
        line_extension_associate.assert_called_once_with(line_extension)
        formatter.to_api.assert_called_once_with(line_extension)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.line_extension.services.get_by_line_id')
    def test_get_extension_associated_to_a_line_with_no_extension(self, line_extension_get_by_line_id):
        line_id = 1
        expected_status_code = 404
        expected_result = ['Line with id=%s does not have an extension' % line_id]

        line_extension_get_by_line_id.side_effect = LineExtensionNotExistsError.from_line_id(line_id)

        result = self.app.get(BASE_URL % line_id)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.line_extension.services.get_by_line_id')
    def test_get_extension_associated_to_a_line(self, line_extension_get_by_line_id):
        line_id = 1
        extension_id = 2
        expected_status_code = 200
        expected_result = {
            u'extension_id': 2,
            u'line_id': 1,
            u'links': [
                {u'href': u'http://localhost/1.1/lines_sip/%d' % line_id,
                 u'rel': u'lines_sip'},
                {u'href': u'http://localhost/1.1/extensions/%d' % extension_id,
                 u'rel': u'extensions'},
            ]
        }

        line_extension_link = LineExtension(extension_id=extension_id,
                                            line_id=line_id)

        line_extension_get_by_line_id.return_value = line_extension_link

        result = self.app.get(BASE_URL % line_id)
        decoded_result = self._serialize_decode(result.data)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(decoded_result, has_entries(expected_result))
