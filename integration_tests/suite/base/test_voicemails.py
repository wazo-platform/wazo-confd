# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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

from . import confd, mocks
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.helpers import (
    context as context_helper,
    voicemail as vm_helper,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)


def test_search_errors():
    url = confd.voicemails.get
    s.search_error_checks(url)


def test_get_errors():
    fake_get = confd.voicemails(999999).get
    s.check_resource_not_found(fake_get, 'Voicemail')


def test_post_errors():
    url = confd.voicemails.post
    error_checks(url)
    error_required_checks(url)


def test_put_errors():
    with fixtures.voicemail() as voicemail:
        fake_put = confd.voicemails(9999999).put
        s.check_resource_not_found(fake_put, 'Voicemail')

        url = confd.voicemails(voicemail['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', 123)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(81))
    s.check_bogus_field_returns_error(url, 'number', 123)
    s.check_bogus_field_returns_error(url, 'number', None)
    s.check_bogus_field_returns_error(url, 'number', 'one')
    s.check_bogus_field_returns_error(url, 'number', '#1234')
    s.check_bogus_field_returns_error(url, 'number', '*1234')
    s.check_bogus_field_returns_error(url, 'number', s.random_string(0))
    s.check_bogus_field_returns_error(url, 'number', s.random_string(41))
    s.check_bogus_field_returns_error(url, 'context', 123)
    s.check_bogus_field_returns_error(url, 'context', None)
    s.check_bogus_field_returns_error(url, 'context', True)
    s.check_bogus_field_returns_error(url, 'password', 123)
    s.check_bogus_field_returns_error(url, 'password', True)
    s.check_bogus_field_returns_error(url, 'password', 'one')
    s.check_bogus_field_returns_error(url, 'password', '#1234')
    s.check_bogus_field_returns_error(url, 'password', '*1234')
    s.check_bogus_field_returns_error(url, 'password', s.random_string(0))
    s.check_bogus_field_returns_error(url, 'password', s.random_string(81))
    s.check_bogus_field_returns_error(url, 'email', 123)
    s.check_bogus_field_returns_error(url, 'email', True)
    s.check_bogus_field_returns_error(url, 'email', s.random_string(81))
    s.check_bogus_field_returns_error(url, 'language', 123)
    s.check_bogus_field_returns_error(url, 'language', True)
    s.check_bogus_field_returns_error(url, 'timezone', 123)
    s.check_bogus_field_returns_error(url, 'timezone', True)
    s.check_bogus_field_returns_error(url, 'max_messages', 'string')
    s.check_bogus_field_returns_error(url, 'max_messages', -1)
    s.check_bogus_field_returns_error(url, 'max_messages', {})
    s.check_bogus_field_returns_error(url, 'max_messages', [])
    s.check_bogus_field_returns_error(url, 'attach_audio', 'false')
    s.check_bogus_field_returns_error(url, 'attach_audio', {})
    s.check_bogus_field_returns_error(url, 'attach_audio', [])
    s.check_bogus_field_returns_error(url, 'delete_messages', 'true')
    s.check_bogus_field_returns_error(url, 'delete_messages', None)
    s.check_bogus_field_returns_error(url, 'delete_messages', {})
    s.check_bogus_field_returns_error(url, 'delete_messages', [])
    s.check_bogus_field_returns_error(url, 'ask_password', 'false')
    s.check_bogus_field_returns_error(url, 'ask_password', None)
    s.check_bogus_field_returns_error(url, 'ask_password', {})
    s.check_bogus_field_returns_error(url, 'ask_password', [])
    s.check_bogus_field_returns_error(url, 'options', 'string')
    s.check_bogus_field_returns_error(url, 'options', 1234)
    s.check_bogus_field_returns_error(url, 'options', True)
    s.check_bogus_field_returns_error(url, 'options', None)
    s.check_bogus_field_returns_error(url, 'options', {})
    s.check_bogus_field_returns_error(url, 'options', ['string'])
    s.check_bogus_field_returns_error(url, 'options', ['string', 'string'])
    s.check_bogus_field_returns_error(url, 'options', [{'string': 'string'}])
    s.check_bogus_field_returns_error(url, 'options', [['string']])
    s.check_bogus_field_returns_error(url, 'options', [[None, None]])
    s.check_bogus_field_returns_error(url, 'options', [['string', 'string', 'string']])
    s.check_bogus_field_returns_error(url, 'options', [['string', 'string'], ['string']])


def error_required_checks(url):
    s.check_missing_required_field_returns_error(url, 'name')
    s.check_missing_required_field_returns_error(url, 'number')
    s.check_missing_required_field_returns_error(url, 'context')


def test_fake_fields():
    with fixtures.voicemailNone as voicemail:
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
                response.assert_match(400, e.not_found(error_field))



def _generate_fields():
    number, context = vm_helper.generate_number_and_context()
    return {'number': number, 'context': context, 'name': 'testvoicemail'}


def test_create_voicemail_with_same_number_and_context():
    with fixtures.voicemail() as voicemail:
        response = confd.voicemails.post(
            name='testvoicemail',
            number=voicemail['number'],
            context=voicemail['context'],
        )
        response.assert_match(400, e.resource_exists('Voicemail'))



def test_create_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT) as in_main:
        response = confd.voicemails.post(context=in_main['name'], wazo_tenant=SUB_TENANT)
        response.assert_status(400)



def test_edit_voicemail_with_same_number_and_context():
    with fixtures.voicemail() as first_voicemail, fixtures.voicemail() as second_voicemail:
        response = confd.voicemails(first_voicemail['id']).put(
            number=second_voicemail['number'],
            context=second_voicemail['context'],
        )
        response.assert_match(400, e.resource_exists('Voicemail'))



def test_search():
    with fixtures.voicemail(
    name="SearchVoicemail",
    email="searchemail@proformatique.com",
    pager="searchpager@proformatique.com",
) as voicemail, fixtures.voicemail(
    name="HiddenVoicemail",
    email="hiddenvoicemail@proformatique.com",
    pager="hiddenpager@proformatique.com",
) as hidden:
        url = confd.voicemails

        searches = {
            'name': 'searchv',
            'number': voicemail['number'],
            'email': 'searche',
            'pager': 'searchp',
        }

        for field, term in searches.items():
            check_search(url, voicemail, hidden, field, term)



def check_search(url, voicemail, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, voicemail[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: voicemail[field]})
    assert_that(response.items, has_item(has_entry('id', voicemail['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_list_multi_tenant():
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as __, fixtures.voicemail(context='main_ctx') as main, fixtures.voicemail(context='sub_ctx') as sub:
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



def test_sorting_offset_limit():
    with fixtures.voicemail(
    name='sort1',
    number='8001',
    email='sort1@example.com',
    pager='sort1@example.com',
) as voicemail1, fixtures.voicemail(
    name='sort2',
    number='8002',
    email='sort2@example.com',
    pager='sort2@example.com',
) as voicemail2:
        url = confd.voicemails.get
        s.check_sorting(url, voicemail1, voicemail2, 'name', 'sort')
        s.check_sorting(url, voicemail1, voicemail2, 'number', '800')
        s.check_sorting(url, voicemail1, voicemail2, 'email', 'sort')
        s.check_sorting(url, voicemail1, voicemail2, 'pager', 'sort')

        s.check_offset(url, voicemail1, voicemail2, 'name', 'sort')
        s.check_offset_legacy(url, voicemail1, voicemail2, 'name', 'sort')

        s.check_limit(url, voicemail1, voicemail2, 'name', 'sort')



def test_list_voicemails():
    with fixtures.voicemail() as first, fixtures.voicemail() as second:
        response = confd.voicemails.get()
        assert_that(response.items, has_items(has_entries(first), has_entries(second)))



def test_get_voicemail():
    with fixtures.voicemail() as voicemail:
        response = confd.voicemails(voicemail['id']).get()
        assert_that(response.item, has_entries(voicemail))
        assert_that(response.item, has_entries(
            users=empty(),
        ))



def test_get_multi_tenant():
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as __, fixtures.voicemail(context='main_ctx') as main, fixtures.voicemail(context='sub_ctx') as sub:
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


def test_create_voicemail_with_all_parameters():
    with fixtures.voicemail_zonemessages(name='eu-fr') as _:
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



def test_edit_voicemail():
    with fixtures.voicemail() as voicemail, fixtures.voicemail_zonemessages(name='eu-fr') as _:
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



@mocks.sysconfd()
def test_edit_number_and_context_moves_voicemail(voicemail):
    with fixtures.voicemail() as sysconfd:
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



def test_edit_multi_tenant():
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as main_ctx, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as _, fixtures.voicemail(context='main_ctx') as main, fixtures.voicemail(context='sub_ctx') as sub:
        response = confd.voicemails(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Voicemail'))

        response = confd.voicemails(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()

        response = confd.voicemails(sub['id']).put(context=main_ctx['name'], wazo_tenant=SUB_TENANT)
        response.assert_status(400)



def test_delete_voicemail():
    with fixtures.voicemail() as voicemail:
        response = confd.voicemails(voicemail['id']).delete()
        response.assert_deleted()



def test_delete_multi_tenant():
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as __, fixtures.voicemail(context='main_ctx') as main, fixtures.voicemail(context='sub_ctx') as sub:
        response = confd.voicemails(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Voicemail'))

        response = confd.voicemails(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()



@mocks.sysconfd()
def test_delete_voicemail_deletes_on_disk(voicemail):
    with fixtures.voicemail() as sysconfd:
        response = confd.voicemails(voicemail['id']).delete()
        response.assert_deleted()

        sysconfd.assert_request(
            '/delete_voicemail',
            query={
                'mailbox': voicemail['number'],
                'context': voicemail['context'],
            }
        )



def test_update_fields_with_null_value():
    with fixtures.voicemail() as voicemail, fixtures.voicemail_zonemessages(name='eu-fr') as _:
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



def test_user_voicemail_edited_bus_event():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user, voicemail):
            routing_key = 'config.users.{}.voicemails.edited'.format(user['uuid'])
            s.check_bus_event(routing_key, confd.voicemails(voicemail['id']).put, {'name': 'bostwana'})
