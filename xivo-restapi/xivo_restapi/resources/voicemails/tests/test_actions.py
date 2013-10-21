# -*- coding: UTF-8 -*-

from mock import patch, Mock
from hamcrest import *
from xivo_restapi.helpers.tests.test_resources import TestResources
from xivo_dao.data_handler.voicemail.model import Voicemail, VoicemailOrder
from xivo_dao.helpers.abstract_model import SearchResult


BASE_URL = "/1.1/voicemails"


class TestVoicemailsAction(TestResources):

    @patch('xivo_dao.data_handler.voicemail.services.get')
    def test_get(self, mock_voicemail_services_get):
        voicemail_id = 3425
        expected_status_code = 200
        expected_result = {
            'id': voicemail_id,
            'name': 'totto',
            'number': '1234',
            'context': 'default',
            'password': '1234passwd',
            'email': 'xivo@avencall.com',
            'language': 'fr_FR',
            'timezone': 'eu-fr',
            'max_messages': 2,
            'attach_audio': True,
            'delete_messages': False,
            'ask_password': False,
            'links': [{
                'href': 'http://localhost/1.1/voicemails/%d' % voicemail_id,
                'rel': 'voicemails'
            }]
        }
        voicemail = Voicemail(id=voicemail_id,
                              name=expected_result['name'],
                              number=expected_result['number'],
                              context=expected_result['context'],
                              password=expected_result['password'],
                              email=expected_result['email'],
                              language=expected_result['language'],
                              timezone=expected_result['timezone'],
                              max_messages=expected_result['max_messages'],
                              attach_audio=expected_result['attach_audio'],
                              delete_messages=expected_result['delete_messages'],
                              ask_password=expected_result['ask_password'])
        mock_voicemail_services_get.return_value = voicemail

        result = self.app.get("%s/%d" % (BASE_URL, voicemail_id))

        mock_voicemail_services_get.assert_called_once_with(voicemail_id)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.voicemail.services.find_all')
    def test_list_voicemails_with_no_voicemails(self, mock_voicemail_services_find_all):
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        voicemails_found = Mock(SearchResult)
        voicemails_found.total = 0
        voicemails_found.items = []
        mock_voicemail_services_find_all.return_value = voicemails_found

        result = self.app.get(BASE_URL)

        mock_voicemail_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.voicemail.services.find_all')
    def test_list_voicemails_with_two_voicemails(self, voicemail_find_all):
        voicemail_id_1 = 123421
        voicemail_id_2 = 235235
        total = 2

        voicemail1 = Voicemail(id=voicemail_id_1,
                               name='10.0.0.1',
                               number='001122334455',
                               context='fasdf',
                               attach_audio=False,
                               delete_messages=False,
                               ask_password=False)
        voicemail2 = Voicemail(id=voicemail_id_2,
                               name='10.0.0.2',
                               number='001122334456',
                               context='dsad',
                               attach_audio=False,
                               delete_messages=False,
                               ask_password=False)

        expected_status_code = 200
        expected_result = {
            'total': total,
            'items': [
                {
                    'id': voicemail1.id,
                    'name': voicemail1.name,
                    'number': voicemail1.number,
                    'context': voicemail1.context,
                    'language': None,
                    'password': None,
                    'email': None,
                    'timezone': None,
                    'max_messages': None,
                    'attach_audio': False,
                    'delete_messages': False,
                    'ask_password': False,
                    'links': [{
                        'href': 'http://localhost/1.1/voicemails/%s' % voicemail1.id,
                        'rel': 'voicemails'
                    }]
                },
                {
                    'id': voicemail2.id,
                    'name': voicemail2.name,
                    'number': voicemail2.number,
                    'context': voicemail2.context,
                    'language': None,
                    'password': None,
                    'email': None,
                    'timezone': None,
                    'max_messages': None,
                    'attach_audio': False,
                    'delete_messages': False,
                    'ask_password': False,
                    'links': [{
                        'href': 'http://localhost/1.1/voicemails/%s' % voicemail2.id,
                        'rel': 'voicemails'
                    }]
                }
            ]
        }

        voicemails_found = Mock(SearchResult)
        voicemails_found.total = total
        voicemails_found.items = [voicemail1, voicemail2]

        voicemail_find_all.return_value = voicemails_found

        result = self.app.get(BASE_URL)

        voicemail_find_all.assert_called_once_with()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.voicemails.actions.extract_find_parameters')
    @patch('xivo_dao.data_handler.voicemail.services.find_all')
    def test_list_voicemails_with_parameters(self, voicemail_find_all, extract_find_parameters):
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }
        query_string = 'skip=532&limit=5432&order=toto&direction=asc&search=abcd'
        request_parameters = {
            'skip': 532,
            'limit': 5432,
            'order': 'toto',
            'direction': 'asc',
            'search': 'abcd'
        }
        extract_find_parameters.return_value = request_parameters

        voicemails_found = Mock(SearchResult)
        voicemails_found.total = 0
        voicemails_found.items = []

        voicemail_find_all.return_value = voicemails_found

        result = self.app.get("%s?%s" % (BASE_URL, query_string))

        extract_find_parameters.assert_called_once_with({
            'name': VoicemailOrder.name,
            'number': VoicemailOrder.number,
            'context': VoicemailOrder.context,
            'email': VoicemailOrder.email,
            'language': VoicemailOrder.language,
            'timezone': VoicemailOrder.timezone
        })
        voicemail_find_all.assert_called_once_with(**request_parameters)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))


    @patch('xivo_restapi.resources.voicemails.actions.formatter')
    @patch('xivo_dao.data_handler.voicemail.services.create')
    def test_create(self, voicemail_services_create, formatter):
        voicemail_id = 123456
        name = 'John Montana'
        number = '10001'
        context = 'default'

        expected_status_code = 201
        expected_result = {
            'id': voicemail_id,
            'name': name,
            'number': number,
            'context': context,
            'links': [{
                'href': 'http://localhost/1.1/voicemails/%d' % voicemail_id,
                'rel': 'voicemails'
            }]
        }

        data = {'name': name,
                'number': number,
                'context': context}

        data_serialized = self._serialize_encode(data)

        voicemail = Mock(Voicemail)
        created_voicemail = Mock(Voicemail)
        created_voicemail.id = voicemail_id
        created_voicemail.name = name
        created_voicemail.number = number
        created_voicemail.context = context

        voicemail_services_create.return_value = created_voicemail
        formatter.to_model.return_value = voicemail
        formatter.to_api.return_value = self._serialize_encode(expected_result)

        result = self.app.post(BASE_URL, data=data_serialized)

        formatter.to_model.assert_called_once_with(data_serialized)
        voicemail_services_create.assert_called_once_with(voicemail)
        formatter.to_api.assert_called_once_with(created_voicemail)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))


    @patch('xivo_dao.data_handler.voicemail.services.get')
    @patch('xivo_dao.data_handler.voicemail.services.delete')
    def test_delete(self, mock_voicemail_services_delete, mock_voicemail_services_get):
        expected_status_code = 204
        expected_data = ''

        voicemail = Mock(Voicemail)
        mock_voicemail_services_get.return_value = voicemail

        result = self.app.delete("%s/1" % BASE_URL)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_data))
        mock_voicemail_services_delete.assert_called_with(voicemail)
