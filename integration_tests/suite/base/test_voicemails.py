# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from hamcrest import (
    all_of,
    assert_that,
    contains,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)

from . import confd
from . import mocks
from ..helpers import fixtures
from ..helpers import associations as a
from ..helpers import scenarios as s
from ..helpers import errors as e
from ..helpers.helpers import voicemail as vm_helper
from ..helpers.helpers import context as context_helper
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)


def test_search_errors():
    url = confd.voicemails.get
    for check in s.search_error_checks(url):
        yield check


def test_get_errors():
    fake_get = confd.voicemails(999999).get
    yield s.check_resource_not_found, fake_get, 'Voicemail'


def test_post_errors():
    url = confd.voicemails.post
    for check in error_checks(url):
        yield check

    for check in error_required_checks(url):
        yield check


@fixtures.voicemail()
def test_put_errors(voicemail):
    fake_put = confd.voicemails(9999999).put
    yield s.check_resource_not_found, fake_put, 'Voicemail'

    url = confd.voicemails(voicemail['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'number', 123
    yield s.check_bogus_field_returns_error, url, 'number', None
    yield s.check_bogus_field_returns_error, url, 'number', 'one'
    yield s.check_bogus_field_returns_error, url, 'number', '#1234'
    yield s.check_bogus_field_returns_error, url, 'number', '*1234'
    yield s.check_bogus_field_returns_error, url, 'number', s.random_string(0)
    yield s.check_bogus_field_returns_error, url, 'number', s.random_string(41)
    yield s.check_bogus_field_returns_error, url, 'context', 123
    yield s.check_bogus_field_returns_error, url, 'context', None
    yield s.check_bogus_field_returns_error, url, 'context', True
    yield s.check_bogus_field_returns_error, url, 'password', 123
    yield s.check_bogus_field_returns_error, url, 'password', True
    yield s.check_bogus_field_returns_error, url, 'password', 'one'
    yield s.check_bogus_field_returns_error, url, 'password', '#1234'
    yield s.check_bogus_field_returns_error, url, 'password', '*1234'
    yield s.check_bogus_field_returns_error, url, 'password', s.random_string(0)
    yield s.check_bogus_field_returns_error, url, 'password', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'email', 123
    yield s.check_bogus_field_returns_error, url, 'email', True
    yield s.check_bogus_field_returns_error, url, 'email', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'language', 123
    yield s.check_bogus_field_returns_error, url, 'language', True
    yield s.check_bogus_field_returns_error, url, 'timezone', 123
    yield s.check_bogus_field_returns_error, url, 'timezone', True
    yield s.check_bogus_field_returns_error, url, 'max_messages', 'string'
    yield s.check_bogus_field_returns_error, url, 'max_messages', -1
    yield s.check_bogus_field_returns_error, url, 'max_messages', {}
    yield s.check_bogus_field_returns_error, url, 'max_messages', []
    yield s.check_bogus_field_returns_error, url, 'attach_audio', 'false'
    yield s.check_bogus_field_returns_error, url, 'attach_audio', {}
    yield s.check_bogus_field_returns_error, url, 'attach_audio', []
    yield s.check_bogus_field_returns_error, url, 'delete_messages', 'true'
    yield s.check_bogus_field_returns_error, url, 'delete_messages', None
    yield s.check_bogus_field_returns_error, url, 'delete_messages', {}
    yield s.check_bogus_field_returns_error, url, 'delete_messages', []
    yield s.check_bogus_field_returns_error, url, 'ask_password', 'false'
    yield s.check_bogus_field_returns_error, url, 'ask_password', None
    yield s.check_bogus_field_returns_error, url, 'ask_password', {}
    yield s.check_bogus_field_returns_error, url, 'ask_password', []
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', 1234
    yield s.check_bogus_field_returns_error, url, 'options', True
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', {}
    yield s.check_bogus_field_returns_error, url, 'options', ['string']
    yield s.check_bogus_field_returns_error, url, 'options', ['string', 'string']
    yield s.check_bogus_field_returns_error, url, 'options', [{'string': 'string'}]
    yield s.check_bogus_field_returns_error, url, 'options', [['string']]
    yield s.check_bogus_field_returns_error, url, 'options', [[None, None]]
    yield s.check_bogus_field_returns_error, url, 'options', [['string', 'string', 'string']]
    yield s.check_bogus_field_returns_error, url, 'options', [['string', 'string'], ['string']]


def error_required_checks(url):
    yield s.check_missing_required_field_returns_error, url, 'name'
    yield s.check_missing_required_field_returns_error, url, 'number'
    yield s.check_missing_required_field_returns_error, url, 'context'


@fixtures.voicemail
def test_fake_fields(voicemail):
    fake = [
        ('context', 'wrongcontext', 'Context'),
        ('language', 'fakelanguage', 'Language'),
        ('timezone', 'faketimezone', 'Timezone')
    ]
    requests = [
        confd.voicemails.post,
        confd.voicemails(voicemail['id']).put,
    ]

    for (field, value, error_field) in fake:
        for request in requests:
            fields = _generate_fields()
            fields[field] = value
            response = request(fields)
            yield response.assert_match, 400, e.not_found(error_field)


def _generate_fields():
    number, context = vm_helper.generate_number_and_context()
    return {'number': number, 'context': context, 'name': 'testvoicemail'}


@fixtures.voicemail()
def test_create_voicemail_with_same_number_and_context(voicemail):
    response = confd.voicemails.post(
        name='testvoicemail',
        number=voicemail['number'],
        context=voicemail['context'],
    )
    response.assert_match(400, e.resource_exists('Voicemail'))


@fixtures.voicemail()
@fixtures.voicemail()
def test_edit_voicemail_with_same_number_and_context(first_voicemail, second_voicemail):
    response = confd.voicemails(first_voicemail['id']).put(
        number=second_voicemail['number'],
        context=second_voicemail['context'],
    )
    response.assert_match(400, e.resource_exists('Voicemail'))


@fixtures.voicemail(name="SearchVoicemail",
                    email="searchemail@proformatique.com",
                    pager="searchpager@proformatique.com")
@fixtures.voicemail(name="HiddenVoicemail",
                    email="hiddenvoicemail@proformatique.com",
                    pager="hiddenpager@proformatique.com")
def test_search(voicemail, hidden):
    url = confd.voicemails

    searches = {
        'name': 'searchv',
        'number': voicemail['number'],
        'email': 'searche',
        'pager': 'searchp',
    }

    for field, term in searches.items():
        yield check_search, url, voicemail, hidden, field, term


def check_search(url, voicemail, hidden, field, term):
    response = url.get(search=term)

    expected_voicemail = has_item(has_entry(field, voicemail[field]))
    hidden_voicemail = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, expected_voicemail)
    assert_that(response.items, hidden_voicemail)

    response = url.get(**{field: voicemail[field]})

    expected_voicemail = has_item(has_entry('id', voicemail['id']))
    hidden_voicemail = is_not(has_item(has_entry('id', hidden['id'])))
    assert_that(response.items, expected_voicemail)
    assert_that(response.items, hidden_voicemail)


@fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT)
@fixtures.voicemail(context='main_ctx')
@fixtures.voicemail(context='sub_ctx')
def test_list_multi_tenant(_, __, main, sub):
    response = confd.voicemails.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(has_item(main), not_(has_item(sub))),
    )

    response = confd.voicemails.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(has_item(sub), not_(has_item(main))),
    )

    response = confd.voicemails.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(main, sub),
    )


@fixtures.voicemail(name='sort1',
                    number='8001',
                    email='sort1@example.com',
                    pager='sort1@example.com')
@fixtures.voicemail(name='sort2',
                    number='8002',
                    email='sort2@example.com',
                    pager='sort2@example.com')
def test_sorting_offset_limit(voicemail1, voicemail2):
    url = confd.voicemails.get
    yield s.check_sorting, url, voicemail1, voicemail2, 'name', 'sort'
    yield s.check_sorting, url, voicemail1, voicemail2, 'number', '800'
    yield s.check_sorting, url, voicemail1, voicemail2, 'email', 'sort'
    yield s.check_sorting, url, voicemail1, voicemail2, 'pager', 'sort'

    yield s.check_offset, url, voicemail1, voicemail2, 'name', 'sort'
    yield s.check_offset_legacy, url, voicemail1, voicemail2, 'name', 'sort'

    yield s.check_limit, url, voicemail1, voicemail2, 'name', 'sort'


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
    assert_that(response.item, has_entries(
        users=empty(),
    ))


@fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT)
@fixtures.voicemail(context='main_ctx')
@fixtures.voicemail(context='sub_ctx')
def test_get_multi_tenant(_, __, main, sub):
    response = confd.voicemails(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Voicemail'))

    response = confd.voicemails(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_voicemail():
    number, context = vm_helper.generate_number_and_context()
    response = confd.voicemails.post(name='minimal', number=number, context=context)

    response.assert_created('voicemails')
    assert_that(
        response.item,
        has_entries(
            name='minimal',
            number=number,
            context=context,
            ask_password=True,
            attach_audio=None,
            delete_messages=False,
            options=contains(),
            tenant_uuid=MAIN_TENANT,
        )
    )


def test_create_voicemails_same_number_different_contexts():
    number, context = vm_helper.new_number_and_context('vmctx1')
    other_context = context_helper.generate_context(name='vmctx2')

    response = confd.voicemails.post(
        name='samenumber1',
        number=number,
        context=context,
    )
    response.assert_ok()

    response = confd.voicemails.post(
        name='samenumber2',
        number=number,
        context=other_context['name'],
    )
    response.assert_ok()


@fixtures.voicemail_zonemessages(name='eu-fr')
def test_create_voicemail_with_all_parameters(_):
    number, context = vm_helper.generate_number_and_context()

    parameters = {
        'name': 'full',
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
        'options': [["saycid", "yes"], ["emailbody", "this\nis\ra\temail|body"]],
    }

    response = confd.voicemails.post(parameters)
    response.assert_created('voicemails')
    assert_that(
        response.item,
        has_entries(
            name='full',
            number=number,
            context=context,
            email='test@example.com',
            pager='test@example.com',
            language='en_US',
            timezone='eu-fr',
            password='1234',
            max_messages=10,
            attach_audio=True,
            ask_password=False,
            delete_messages=True,
            enabled=True,
            options=has_items(["saycid", "yes"], ["emailbody", "this\nis\ra\temail|body"]),
        )
    )


@fixtures.voicemail()
@fixtures.voicemail_zonemessages(name='eu-fr')
def test_edit_voicemail(voicemail, _):
    number, context = vm_helper.new_number_and_context('vmctxedit')

    parameters = {
        'name': 'edited',
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
        'options': [["saycid", "yes"], ["emailbody", "this\nis\ra\temail|body"]],
    }

    url = confd.voicemails(voicemail['id'])

    response = url.put(parameters)
    response.assert_updated()

    response = url.get()
    assert_that(
        response.item,
        has_entries(
            name='edited',
            number=number,
            context=context,
            email='test@example.com',
            pager='test@example.com',
            language='en_US',
            timezone='eu-fr',
            password='1234',
            max_messages=10,
            attach_audio=True,
            ask_password=False,
            delete_messages=True,
            enabled=False,
            options=has_items(["saycid", "yes"], ["emailbody", "this\nis\ra\temail|body"]),
        )
    )


@fixtures.voicemail()
@mocks.sysconfd()
def test_edit_number_and_context_moves_voicemail(voicemail, sysconfd):
    number, context = vm_helper.new_number_and_context('vmctxmove')

    response = confd.voicemails(voicemail['id']).put(number=number, context=context)
    response.assert_updated()

    sysconfd.assert_request(
        '/move_voicemail',
        query={
            'old_mailbox': voicemail['number'],
            'old_context': voicemail['context'],
            'new_mailbox': number,
            'new_context': context,
        },
    )


@fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT)
@fixtures.voicemail(context='main_ctx')
@fixtures.voicemail(context='sub_ctx')
def test_edit_multi_tenant(_, __, main, sub):
    response = confd.voicemails(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Voicemail'))

    response = confd.voicemails(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.voicemail()
def test_delete_voicemail(voicemail):
    response = confd.voicemails(voicemail['id']).delete()
    response.assert_deleted()


@fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT)
@fixtures.voicemail(context='main_ctx')
@fixtures.voicemail(context='sub_ctx')
def test_delete_multi_tenant(_, __, main, sub):
    response = confd.voicemails(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Voicemail'))

    response = confd.voicemails(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.voicemail()
@mocks.sysconfd()
def test_delete_voicemail_deletes_on_disk(voicemail, sysconfd):
    response = confd.voicemails(voicemail['id']).delete()
    response.assert_deleted()

    sysconfd.assert_request(
        '/delete_voicemail',
        query={
            'mailbox': voicemail['number'],
            'context': voicemail['context'],
        }
    )


@fixtures.voicemail()
@fixtures.voicemail_zonemessages(name='eu-fr')
def test_update_fields_with_null_value(voicemail, _):
    number, context = vm_helper.generate_number_and_context()

    response = confd.voicemails.post(
        name='nullfields',
        number=number,
        context=context,
        password='1234',
        email='test@example.com',
        pager='test@example.com',
        language='en_US',
        timezone='eu-fr',
        max_messages=10,
        attach_audio=True,
    )

    url = confd.voicemails(response.item['id'])
    fields = {
        'password': None,
        'email': None,
        'pager': None,
        'language': None,
        'timezone': None,
        'max_messages': None,
        'attach_audio': None,
    }
    response = url.put(**fields)
    response.assert_updated()

    response = url.get()
    assert_that(response.item, has_entries(fields))


@fixtures.user()
@fixtures.voicemail()
def test_user_voicemail_edited_bus_event(user, voicemail):
    with a.user_voicemail(user, voicemail):
        routing_key = 'config.users.{}.voicemails.edited'.format(user['uuid'])
        yield s.check_bus_event, routing_key, confd.voicemails(voicemail['id']).put, {'name': 'bostwana'}
