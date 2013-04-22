# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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

from mock import Mock
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.service_data_model.sdm_exception import \
    IncorrectParametersException
from xivo_restapi.rest import rest_encoder
from xivo_restapi.rest.helpers import global_helper
from xivo_restapi.rest.tests import instance_user_management, instance_user_sdm, \
    mock_user_sdm
from xivo_restapi.restapi_config import RestAPIConfig
from xivo_restapi.services.utils.exceptions import NoSuchElementException, \
    ProvdError, VoicemailExistsException, SysconfdError
import unittest


class TestAPIUsers(unittest.TestCase):

    def setUp(self):
        self.instance_user_management = instance_user_management
        self.user_sdm = instance_user_sdm
        from xivo_restapi.rest import flask_http_server
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    def test_list_users(self):
        status = "200 OK"
        user1 = UserFeatures()
        user1.firstname = 'test1'
        user2 = UserFeatures()
        user2.firstname = 'test2'
        expected_list = [user1, user2]
        expected_result = {"items": expected_list}
        self.instance_user_management.get_all_users.return_value = expected_list
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/',
                              '')

        self.instance_user_management.get_all_users.assert_any_call()
        self.assertEquals(result.status, status)
        self.assertEquals(rest_encoder.encode(expected_result), result.data)

    def test_list_users_error(self):
        status = "500 INTERNAL SERVER ERROR"

        def mock_get_all_users():
            raise Exception()

        self.instance_user_management.get_all_users\
                    .side_effect = mock_get_all_users
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/')

        self.instance_user_management.get_all_users.assert_any_call()
        self.assertEqual(result.status, status)
        self.instance_user_management.get_all_users.side_effect = None

    def test_get(self):
        status = "200 OK"
        user1 = UserFeatures()
        user1.firstname = 'test1'
        self.instance_user_management.get_user.return_value = user1
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1',
                              '')

        self.instance_user_management.get_user.assert_called_with(1)
        self.assertEquals(result.status, status)
        self.assertEquals(rest_encoder.encode(user1), result.data)

    def test_get_error(self):
        status = "500 INTERNAL SERVER ERROR"

        def mock_get_user():
            raise Exception()

        self.instance_user_management.get_user.side_effect = mock_get_user
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')

        self.instance_user_management.get_user.assert_called_with(1)
        self.assertEqual(result.status, status)
        self.instance_user_management.get_user.side_effect = None

    def test_get_not_found(self):
        status = "404 NOT FOUND"

        def mock_get_user(userid):
            raise NoSuchElementException("No such user")

        self.instance_user_management.get_user.side_effect = mock_get_user
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')

        self.instance_user_management.get_user.assert_called_with(1)
        self.assertEqual(result.status, status)
        self.instance_user_management.get_user.side_effect = None

    def test_create(self):
        status = "201 CREATED"
        data = {u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}
        self.instance_user_management.create_user.return_value = True
        global_helper.create_class_instance = Mock()
        global_helper.create_class_instance.return_value = self.user_sdm
        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/',
                              data=rest_encoder.encode(data))
        self.assertEqual(result.status, status)
        global_helper.create_class_instance.assert_called_with(mock_user_sdm, data)  # @UndefinedVariable
        self.instance_user_management.create_user.assert_called_with(self.user_sdm)

    def test_create_error(self):
        status = "500 INTERNAL SERVER ERROR"
        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'description': 'éà":;'}

        def mock_create_user(user):
            raise Exception()

        self.instance_user_management.create_user.side_effect = mock_create_user
        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/',
                              data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.instance_user_management.create_user.side_effect = None

    def test_create_request_error(self):
        status = "400 BAD REQUEST"
        expected_data = "Incorrect parameters sent: unexisting_field"
        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'unexisting_field': 'value'}

        def mock_validate(data):
            raise IncorrectParametersException("unexisting_field")

        self.user_sdm.validate.side_effect = mock_validate
        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/',
                              data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        received_data = rest_encoder.decode(result.data)
        self.assertEquals(expected_data, received_data[0])
        self.user_sdm.validate.side_effect = None

    def test_edit(self):
        status = "200 OK"
        data = {u'id': 2,
                u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}
        self.instance_user_management.edit_user.return_value = True
        self.user_sdm.validate.return_value = True
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1',
                              data=rest_encoder.encode(data))
        self.assertEqual(result.status, status)
        self.user_sdm.validate.assert_called_with(data)
        self.instance_user_management.edit_user.assert_called_with(1, data)

    def test_edit_error(self):
        status = "500 INTERNAL SERVER ERROR"
        data = {u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}

        def mock_edit_user(userid, data):
            raise Exception()

        self.instance_user_management.edit_user.side_effect = mock_edit_user
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1',
                              data=rest_encoder.encode(data))
        self.user_sdm.validate.assert_called_with(data)
        self.assertEqual(status, result.status)
        self.instance_user_management.edit_user.side_effect = None

    def test_edit_request_error(self):
        status = "400 BAD REQUEST"
        expected_data = "Incorrect parameters sent: unexisting_field"
        data = {u'firstname': u'André',
                u'lastname': u'Dupond',
                u'unexisting_field': u'value'}

        def mock_validate_data(data):
            raise IncorrectParametersException("unexisting_field")

        self.user_sdm.validate.side_effect = mock_validate_data
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1',
                              data=rest_encoder.encode(data))
        self.assertEquals(result.status, status)
        received_data = rest_encoder.decode(result.data)
        self.assertEquals(received_data[0], expected_data)
        self.user_sdm.validate.assert_called_with(data)
        self.instance_user_management.edit_user.side_effect = None

    def test_edit_not_found(self):
        status = "404 NOT FOUND"
        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'description': 'éà":;'}

        def mock_edit_user(userid, data):
            raise NoSuchElementException('')

        self.instance_user_management.edit_user.side_effect = mock_edit_user
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1',
                              data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.instance_user_management.edit_user.side_effect = None

    def test_delete_success(self):
        status = "200 OK"
        self.instance_user_management.delete_user.return_value = True
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')
        self.assertEqual(result.status, status)
        self.instance_user_management.delete_user.assert_called_with(1, False)

    def test_delete_not_found(self):
        status = "404 NOT FOUND"

        def mock_delete(userid, delete_voicemail):
            raise NoSuchElementException("")

        self.instance_user_management.delete_user.side_effect = mock_delete
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')
        self.assertEqual(result.status, status)
        self.instance_user_management.delete_user.assert_called_with(1, False)

        self.instance_user_management.delete_user.side_effect = None

    def test_delete_provd_error(self):
        status = "500 INTERNAL SERVER ERROR"

        def mock_delete(userid, delete_voicemail):
            raise ProvdError("sample error")

        self.instance_user_management.delete_user.side_effect = mock_delete
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')
        self.instance_user_management.delete_user.side_effect = None
        self.assertEqual(result.status, status)
        data = rest_encoder.decode(result.data)
        self.assertEquals("The user was deleted but the device could not be reconfigured " + \
                          "(provd error: sample error)", data[0])
        self.instance_user_management.delete_user.assert_called_with(1, False)

    def test_delete_voicemail_exists(self):
        status = "412 PRECONDITION FAILED"

        def mock_delete(userid, delete_voicemail):
            raise VoicemailExistsException()

        self.instance_user_management.delete_user.side_effect = mock_delete
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')
        self.instance_user_management.delete_user.side_effect = None
        self.assertEqual(result.status, status)
        data = rest_encoder.decode(result.data)
        self.assertEquals("Cannot remove a user with a voicemail. Delete the voicemail or dissociate it from the user.",
                          data[0])
        self.instance_user_management.delete_user.assert_called_with(1, False)

    def test_delete_force_voicemail_deletion(self):
        status = "200 OK"
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1?deleteVoicemail')
        self.assertEqual(result.status, status)
        self.instance_user_management.delete_user.assert_called_with(1, True)

    def test_delete_sysconfd_error(self):
        status = "500 INTERNAL SERVER ERROR"

        self.instance_user_management.delete_user.side_effect = SysconfdError("sample error")
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')
        self.instance_user_management.delete_user.side_effect = None
        self.assertEqual(result.status, status)
        data = rest_encoder.decode(result.data)
        self.assertEquals("The user was deleted but the voicemail content could not be removed  " + \
                          "(sysconfd error: sample error)", data[0])
        self.instance_user_management.delete_user.assert_called_with(1, False)
