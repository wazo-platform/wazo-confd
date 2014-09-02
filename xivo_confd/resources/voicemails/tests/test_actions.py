# -*- coding: UTF-8 -*-

from mock import patch
from xivo_confd.helpers.tests.test_resources import TestResources
from xivo_dao.data_handler.voicemail.model import Voicemail
from xivo_dao.data_handler.utils.search import SearchResult


BASE_URL = "/1.1/voicemails"


class TestVoicemailsAction(TestResources):

    def setUp(self):
        super(TestVoicemailsAction, self).setUp()
        self.voicemail = Voicemail(id=3245,
                                   name='myvoicemail',
                                   number='1234',
                                   context='default',
                                   password='1234passwd',
                                   email='xivo@avencall.com',
                                   language='fr_FR',
                                   timezone='eu-fr',
                                   max_messages=2,
                                   attach_audio=False,
                                   delete_messages=False,
                                   ask_password=True)

    def build_item(self, voicemail):
        item = {
            'id': voicemail.id,
            'name': voicemail.name,
            'number': voicemail.number,
            'context': voicemail.context,
            'password': voicemail.password,
            'email': voicemail.email,
            'language': voicemail.language,
            'timezone': voicemail.timezone,
            'max_messages': voicemail.max_messages,
            'attach_audio': voicemail.attach_audio,
            'delete_messages': voicemail.delete_messages,
            'ask_password': voicemail.ask_password,
            'links': [{
                'href': 'http://localhost/1.1/voicemails/%d' % voicemail.id,
                'rel': 'voicemails'
            }]
        }

        return item

    @patch('xivo_dao.data_handler.voicemail.services.get')
    def test_get(self, mock_voicemail_services_get):
        mock_voicemail_services_get.return_value = self.voicemail

        expected_result = self.build_item(self.voicemail)

        result = self.app.get("%s/%d" % (BASE_URL, self.voicemail.id))

        self.assert_response_for_get(result, expected_result)
        mock_voicemail_services_get.assert_called_once_with(self.voicemail.id)

    @patch('xivo_dao.data_handler.voicemail.services.search')
    def test_list_voicemails_with_no_voicemails(self, mock_voicemail_services_search):
        mock_voicemail_services_search.return_value = SearchResult(total=0, items=[])

        expected_result = {'total': 0, 'items': []}

        result = self.app.get(BASE_URL)

        self.assert_response_for_list(result, expected_result)
        mock_voicemail_services_search.assert_any_call()

    @patch('xivo_dao.data_handler.voicemail.services.search')
    def test_list_voicemails_with_two_voicemails(self, voicemail_search):
        voicemail1 = Voicemail(id=123421,
                               name='10.0.0.1',
                               number='001122334455',
                               context='fasdf',
                               attach_audio=False,
                               delete_messages=False,
                               ask_password=False)
        voicemail2 = Voicemail(id=235235,
                               name='10.0.0.2',
                               number='001122334456',
                               context='dsad',
                               attach_audio=False,
                               delete_messages=False,
                               ask_password=False)

        voicemail_search.return_value = SearchResult(total=2, items=[voicemail1, voicemail2])

        expected_result = {'total': 2, 'items': [self.build_item(voicemail1),
                                                 self.build_item(voicemail2)]}

        result = self.app.get(BASE_URL)

        self.assert_response_for_list(result, expected_result)
        voicemail_search.assert_called_once_with()

    @patch('xivo_dao.data_handler.voicemail.services.search')
    def test_list_voicemails_with_parameters(self, voicemail_search):
        voicemail_search.return_value = SearchResult(total=0, items=[])

        expected_result = {'total': 0, 'items': []}

        query_string = 'skip=532&limit=5432&order=email&direction=asc&search=abcd'
        request_parameters = {
            'skip': 532,
            'limit': 5432,
            'order': 'email',
            'direction': 'asc',
            'search': 'abcd'
        }

        result = self.app.get("%s?%s" % (BASE_URL, query_string))

        self.assert_response_for_list(result, expected_result)
        voicemail_search.assert_called_once_with(**request_parameters)

    @patch('xivo_dao.data_handler.voicemail.services.create')
    def test_create(self, voicemail_services_create):
        voicemail_services_create.return_value = self.voicemail

        expected_result = self.build_item(self.voicemail)

        created_voicemail = Voicemail(name=self.voicemail.name,
                                      number=self.voicemail.number,
                                      context=self.voicemail.context)

        data = {'name': self.voicemail.name,
                'number': self.voicemail.number,
                'context': self.voicemail.context}
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        self.assert_response_for_create(result, expected_result)
        voicemail_services_create.assert_called_once_with(created_voicemail)

    @patch('xivo_dao.data_handler.voicemail.services.get')
    @patch('xivo_dao.data_handler.voicemail.services.edit')
    def test_edit(self, voicemail_services_edit, voicemail_services_get):
        voicemail_services_get.return_value = self.voicemail

        updated_voicemail = Voicemail(id=3245,
                                      name='toto',
                                      number='12345',
                                      context='mycontext',
                                      password='1234passwd',
                                      email='xivo@avencall.com',
                                      language='fr_FR',
                                      timezone='eu-fr',
                                      max_messages=2,
                                      attach_audio=False,
                                      delete_messages=False,
                                      ask_password=True)
        data = {
            'name': 'toto',
            'number': '12345',
            'context': 'mycontext'
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.put("%s/%s" % (BASE_URL, self.voicemail.id),
                              data=data_serialized)

        self.assert_response_for_update(result)
        voicemail_services_get.assert_called_once_with(self.voicemail.id)
        voicemail_services_edit.assert_called_once_with(updated_voicemail)

    @patch('xivo_dao.data_handler.voicemail.services.get')
    @patch('xivo_dao.data_handler.voicemail.services.delete')
    def test_delete(self, mock_voicemail_services_delete, mock_voicemail_services_get):
        mock_voicemail_services_get.return_value = self.voicemail

        result = self.app.delete("%s/%s" % (BASE_URL, self.voicemail.id))

        self.assert_response_for_delete(result)
        mock_voicemail_services_get.assert_called_once_with(self.voicemail.id)
        mock_voicemail_services_delete.assert_called_with(self.voicemail)
