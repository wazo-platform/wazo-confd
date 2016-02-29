
from test_api import confd
from test_api import config
from test_api import fixtures
from test_api import mocks
from test_api import scenarios as s
from test_api import errors as e

from test_api.helpers import voicemail as vm_helper
from test_api.helpers import context as context_helper

from hamcrest import assert_that, has_items, contains, has_entry, has_entries, has_item, is_not


REQUIRED = ['name', 'number', 'context']

BOGUS = [
    ('name', 123, 'unicode string'),
    ('number', 123, 'unicode string'),
    ('number', 'fakenumber', 'numeric string'),
    ('context', 123, 'unicode string'),
    ('password', 123, 'unicode string'),
    ('password', 'fakepassword', 'numeric string'),
    ('password', 123, 'unicode string'),
    ('email', 123, 'unicode string'),
    ('language', 123, 'unicode string'),
    ('timezone', 123, 'unicode string'),
    ('max_messages', '3', 'integer'),
    ('attach_audio', 'true', 'boolean'),
    ('delete_messages', 'false', 'boolean'),
    ('ask_password', 'true', 'boolean'),
    ('options', '999', 'list of paired string tuples')
]

FAKE = [
    ('context', 'wrongcontext', 'Context'),
    ('language', 'fakelanguage', 'Language'),
    ('timezone', 'faketimezone', 'Timezone')
]


class TestVoicemailResource(s.GetScenarios, s.CreateScenarios, s.EditScenarios, s.DeleteScenarios):

    url = "/voicemails"
    resource = "Voicemail"
    required = REQUIRED
    bogus_fields = BOGUS

    def create_resource(self):
        voicemail = vm_helper.generate_voicemail()
        return voicemail['id']

    def post_resource(self, parameters):
        fields = _generate_fields()
        fields.update(parameters)
        return confd.voicemails.post(fields)


def _generate_fields():
    number, context = vm_helper.generate_number_and_context()
    return {'number': number, 'context': context, 'name': 'testvoicemail'}


@fixtures.voicemail
def test_fake_fields(voicemail):
    requests = (confd.voicemails.post,
                confd.voicemails(voicemail['id']).put)

    for (field, value, error_field) in FAKE:
        for request in requests:
            fields = _generate_fields()
            fields[field] = value
            response = request(fields)
            yield response.assert_match, 400, e.not_found(error_field)


def digit_field_checks(url):
    yield s.check_bogus_field_returns_error, url, 'number', 'one'
    yield s.check_bogus_field_returns_error, url, 'number', '#1234'
    yield s.check_bogus_field_returns_error, url, 'number', '*1234'
    yield s.check_bogus_field_returns_error, url, 'password', 'one'
    yield s.check_bogus_field_returns_error, url, 'password', '#1234'
    yield s.check_bogus_field_returns_error, url, 'password', '*1234'


def test_validation_on_digit_fields():
    number = vm_helper.find_available_number()
    url = confd.voicemails(number=number,
                           name="test",
                           context=config.CONTEXT).post

    for check in digit_field_checks(url):
        yield check

    with fixtures.voicemail() as voicemail:
        url = confd.voicemails(voicemail['id']).put
        for check in digit_field_checks(url):
            yield check


@fixtures.voicemail()
def test_create_voicemail_with_same_number_and_context(voicemail):
    response = confd.voicemails.post(name='testvoicemail',
                                     number=voicemail['number'],
                                     context=voicemail['context'])
    response.assert_match(400, e.resource_exists('Voicemail'))


@fixtures.voicemail()
@fixtures.voicemail()
def test_edit_voicemail_with_same_number_and_context(first_voicemail, second_voicemail):
    response = confd.voicemails(first_voicemail['id']).put(number=second_voicemail['number'],
                                                           context=second_voicemail['context'])
    response.assert_match(400, e.resource_exists('Voicemail'))


@fixtures.voicemail(name="SearchVoicemail",
                    email="searchemail@proformatique.com",
                    pager="searchpager@proformatique.com")
@fixtures.voicemail(name="HiddenVoicemail",
                    email="hiddenvoicemail@proformatique.com",
                    pager="hiddenpager@proformatique.com")
def test_search_voicemail(voicemail, hidden):
    url = confd.voicemails

    searches = {'name': 'searchv',
                'number': voicemail['number'],
                'email': 'searche',
                'pager': 'searchp'}

    for field, term in searches.items():
        yield check_search, url, voicemail, hidden, field, term


def check_search(url, device, hidden, field, term):
    response = url.get(search=term)

    expected_device = has_item(has_entry(field, device[field]))
    hidden_device = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, expected_device)
    assert_that(response.items, hidden_device)


@fixtures.voicemail()
@fixtures.voicemail()
def test_list_voicemails(first, second):
    response = confd.voicemails.get()
    expected = has_items(has_entries(first), has_entries(second))
    assert_that(response.items, expected)


@fixtures.voicemail()
def test_get_voicemail(voicemail):
    response = confd.voicemails(voicemail['id']).get()
    assert_that(response.item, has_entries(voicemail))


def test_create_minimal_voicemail():
    number, context = vm_helper.generate_number_and_context()
    response = confd.voicemails.post(name='minimal',
                                     number=number,
                                     context=context)

    response.assert_created('voicemails')
    assert_that(response.item, has_entries({'name': 'minimal',
                                            'number': number,
                                            'context': context,
                                            'ask_password': True,
                                            'attach_audio': None,
                                            'delete_messages': False,
                                            'options': contains()}))


def test_create_voicemails_same_number_different_contexts():
    number, context = vm_helper.new_number_and_context('vmctx1')
    other_context = context_helper.new_context('vmctx2')

    response = confd.voicemails.post(name='samenumber1',
                                     number=number,
                                     context=context)
    response.assert_ok()

    response = confd.voicemails.post(name='samenumber2',
                                     number=number,
                                     context=other_context)
    response.assert_ok()


def test_create_voicemail_with_all_parameters():
    number, context = vm_helper.generate_number_and_context()

    parameters = {'name': 'full',
                  'number': number,
                  'context': context,
                  'email': 'test@example.com',
                  'pager': 'test@example.com',
                  'language': 'en_US',
                  'timezone': 'eu-fr',
                  'password': '1234',
                  'max_messages': 10,
                  'attach_audio': True,
                  'ask_password': False,
                  'delete_messages': True,
                  'enabled': True,
                  'options': [["saycid", "yes"],
                              ["emailbody", "this\nis\ra\temail|body"]]}

    expected = has_entries({'name': 'full',
                            'number': number,
                            'context': context,
                            'email': 'test@example.com',
                            'pager': 'test@example.com',
                            'language': 'en_US',
                            'timezone': 'eu-fr',
                            'password': '1234',
                            'max_messages': 10,
                            'attach_audio': True,
                            'ask_password': False,
                            'delete_messages': True,
                            'enabled': True,
                            'options': has_items(["saycid", "yes"],
                                                 ["emailbody", "this\nis\ra\temail|body"])
                            })

    response = confd.voicemails.post(parameters)
    response.assert_created('voicemails')
    assert_that(response.item, expected)


@fixtures.voicemail()
def test_edit_voicemail(voicemail):
    number, context = vm_helper.new_number_and_context('vmctxedit')

    parameters = {'name': 'edited',
                  'number': number,
                  'context': context,
                  'email': 'test@example.com',
                  'pager': 'test@example.com',
                  'language': 'en_US',
                  'timezone': 'eu-fr',
                  'password': '1234',
                  'max_messages': 10,
                  'attach_audio': True,
                  'ask_password': False,
                  'delete_messages': True,
                  'enabled': False,
                  'options': [["saycid", "yes"],
                              ["emailbody", "this\nis\ra\temail|body"]]}

    expected = has_entries({'name': 'edited',
                            'number': number,
                            'context': context,
                            'email': 'test@example.com',
                            'pager': 'test@example.com',
                            'language': 'en_US',
                            'timezone': 'eu-fr',
                            'password': '1234',
                            'max_messages': 10,
                            'attach_audio': True,
                            'ask_password': False,
                            'delete_messages': True,
                            'enabled': False,
                            'options': has_items(["saycid", "yes"],
                                                 ["emailbody", "this\nis\ra\temail|body"])
                            })

    url = confd.voicemails(voicemail['id'])

    response = url.put(parameters)
    response.assert_updated()

    response = url.get()
    assert_that(response.item, expected)


@fixtures.voicemail()
@mocks.sysconfd()
def test_edit_number_and_context_moves_voicemail(voicemail, sysconfd):
    number, context = vm_helper.new_number_and_context('vmctxmove')

    response = confd.voicemails(voicemail['id']).put(number=number,
                                                     context=context)
    response.assert_updated()

    sysconfd.assert_request('/move_voicemail',
                            query={'old_mailbox': voicemail['number'],
                                   'old_context': voicemail['context'],
                                   'new_mailbox': number,
                                   'new_context': context})


@fixtures.voicemail()
def test_delete_voicemail(voicemail):
    response = confd.voicemails(voicemail['id']).delete()
    response.assert_deleted()


@fixtures.voicemail()
@mocks.sysconfd()
def test_delete_voicemail_deletes_on_disk(voicemail, sysconfd):
    response = confd.voicemails(voicemail['id']).delete()
    response.assert_deleted()

    sysconfd.assert_request('/delete_voicemail',
                            query={'mailbox': voicemail['number'],
                                   'context': voicemail['context']})


@fixtures.voicemail()
def test_update_fields_with_null_value(voicemail):
    number, context = vm_helper.generate_number_and_context()

    response = confd.voicemails.post(name='nullfields',
                                     number=number,
                                     context=context,
                                     password='1234',
                                     email='test@example.com',
                                     pager='test@example.com',
                                     language='en_US',
                                     timezone='eu-fr',
                                     max_messages=10,
                                     attach_audio=True)

    url = confd.voicemails(response.item['id'])
    response = url.put(password=None,
                       email=None,
                       pager=None,
                       language=None,
                       timezone=None,
                       max_messages=None,
                       attach_audio=None)
    response.assert_updated()

    response = url.get()
    assert_that(response.item, has_entries({'password': None,
                                            'email': None,
                                            'language': None,
                                            'timezone': None,
                                            'max_messages': None,
                                            'attach_audio': None}))
