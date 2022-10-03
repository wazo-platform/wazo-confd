# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    greater_than,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    none,
    not_,
    raises,
    calling,
)
from wazo_test_helpers.hamcrest.uuid_ import uuid_

from . import confd, auth as authentication
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    helpers as h,
    scenarios as s,
    helpers as h,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
    gen_group_exten,
    CONTEXT,
    INCALL_CONTEXT,
)
from requests.exceptions import HTTPError

FULL_USER = {
    "firstname": "Jôhn",
    "lastname": "Smêth",
    "username": "jsmeth",
    "email": "jsmeth@smeth.com",
    "mobile_phone_number": "+4185551234*2",
    "userfield": "userfield",
    "caller_id": '"Jôhnny Smith" <4185551234>',
    "outgoing_caller_id": '"Johnny" <123>',
    "music_on_hold": "default",
    "language": "fr_FR",
    "timezone": "America/Montreal",
    "preprocess_subroutine": "preprocess_subroutine",
    "password": "password",
    "description": "John's description",
    "supervision_enabled": False,
    "call_transfer_enabled": False,
    "dtmf_hangup_enabled": True,
    "call_record_outgoing_external_enabled": True,
    "call_record_outgoing_internal_enabled": True,
    "call_record_incoming_external_enabled": True,
    "call_record_incoming_internal_enabled": True,
    "online_call_record_enabled": True,
    "call_permission_password": '1234',
    "enabled": False,
    "ring_seconds": 60,
    "simultaneous_calls": 10,
    "subscription_type": 1,
}

NULL_USER = {
    "firstname": "Jôhn",
    "lastname": None,
    "username": None,
    "email": None,
    "mobile_phone_number": None,
    "userfield": None,
    "outgoing_caller_id": None,
    "music_on_hold": None,
    "language": None,
    "timezone": None,
    "preprocess_subroutine": None,
    "password": None,
    "description": None,
    "supervision_enabled": True,
    "call_transfer_enabled": True,
    "dtmf_hangup_enabled": False,
    "call_record_outgoing_external_enabled": False,
    "call_record_outgoing_internal_enabled": False,
    "call_record_incoming_external_enabled": False,
    "call_record_incoming_internal_enabled": False,
    "online_call_record_enabled": False,
    "call_permission_password": None,
    "enabled": True,
    "ring_seconds": 30,
    "simultaneous_calls": 5,
}

AUTH_USER = {
    "username": "john",
    "password": "secret",
}


def test_search_errors():
    url = confd.users.get
    for check in s.search_error_checks(url):
        yield check


def test_head_errors():
    response = confd.users(999999).head()
    response.assert_status(404)


def test_get_errors():
    fake_get = confd.users(999999).get
    yield s.check_resource_not_found, fake_get, 'User'


def test_post_errors():
    empty_post = confd.users.post
    user_post = confd.users(firstname="Jôhn").post

    yield s.check_missing_required_field_returns_error, empty_post, 'firstname'
    for check in error_checks(user_post):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'firstname', 123
    yield s.check_bogus_field_returns_error, url, 'firstname', None
    yield s.check_bogus_field_returns_error, url, 'firstname', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'firstname', {}
    yield s.check_bogus_field_returns_error, url, 'firstname', []
    yield s.check_bogus_field_returns_error, url, 'lastname', 123
    yield s.check_bogus_field_returns_error, url, 'lastname', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'lastname', {}
    yield s.check_bogus_field_returns_error, url, 'lastname', []
    yield s.check_bogus_field_returns_error, url, 'email', s.random_string(255)
    yield s.check_bogus_field_returns_error, url, 'email', 123
    yield s.check_bogus_field_returns_error, url, 'email', 'invalid_email'
    yield s.check_bogus_field_returns_error, url, 'email', {}
    yield s.check_bogus_field_returns_error, url, 'email', []
    yield s.check_bogus_field_returns_error, url, 'timezone', 123
    yield s.check_bogus_field_returns_error, url, 'timezone', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'timezone', {}
    yield s.check_bogus_field_returns_error, url, 'timezone', []
    yield s.check_bogus_field_returns_error, url, 'language', 123
    yield s.check_bogus_field_returns_error, url, 'language', 'klingon'
    yield s.check_bogus_field_returns_error, url, 'language', {}
    yield s.check_bogus_field_returns_error, url, 'language', []
    yield s.check_bogus_field_returns_error, url, 'description', 123
    yield s.check_bogus_field_returns_error, url, 'description', {}
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'caller_id', 123
    yield s.check_bogus_field_returns_error, url, 'caller_id', 'invalid_regex'
    yield s.check_bogus_field_returns_error, url, 'caller_id', s.random_string(161)
    yield s.check_bogus_field_returns_error, url, 'caller_id', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id', []
    yield s.check_bogus_field_returns_error, url, 'outgoing_caller_id', 123
    yield s.check_bogus_field_returns_error, url, 'outgoing_caller_id', s.random_string(
        81
    )
    yield s.check_bogus_field_returns_error, url, 'outgoing_caller_id', {}
    yield s.check_bogus_field_returns_error, url, 'outgoing_caller_id', []
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', 123
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', 'invalid_regex'
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', '123abcd'
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', s.random_string(
        81
    )
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', {}
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', []
    yield s.check_bogus_field_returns_error, url, 'username', 123
    yield s.check_bogus_field_returns_error, url, 'username', 'invalid_régex'
    yield s.check_bogus_field_returns_error, url, 'username', s.random_string(1)
    yield s.check_bogus_field_returns_error, url, 'username', s.random_string(255)
    yield s.check_bogus_field_returns_error, url, 'username', {}
    yield s.check_bogus_field_returns_error, url, 'username', []
    yield s.check_bogus_field_returns_error, url, 'password', 123
    yield s.check_bogus_field_returns_error, url, 'password', 'invalid_régex'
    yield s.check_bogus_field_returns_error, url, 'password', s.random_string(3)
    yield s.check_bogus_field_returns_error, url, 'password', s.random_string(65)
    yield s.check_bogus_field_returns_error, url, 'password', {}
    yield s.check_bogus_field_returns_error, url, 'password', []
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', 123
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', {}
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(
        40
    )
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'userfield', 123
    yield s.check_bogus_field_returns_error, url, 'userfield', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'userfield', {}
    yield s.check_bogus_field_returns_error, url, 'userfield', []
    yield s.check_bogus_field_returns_error, url, 'caller_id', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'caller_id', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id', s.random_string(161)
    yield s.check_bogus_field_returns_error, url, 'caller_id', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id', []
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', []
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_enabled', []
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', []
    yield s.check_bogus_field_returns_error, url, 'call_record_incoming_external_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'call_record_incoming_external_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'call_record_incoming_external_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'call_record_incoming_external_enabled', []
    yield s.check_bogus_field_returns_error, url, 'call_record_incoming_internal_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'call_record_incoming_internal_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'call_record_incoming_internal_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'call_record_incoming_internal_enabled', []
    yield s.check_bogus_field_returns_error, url, 'call_record_outgoing_internal_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'call_record_outgoing_internal_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'call_record_outgoing_internal_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'call_record_outgoing_internal_enabled', []
    yield s.check_bogus_field_returns_error, url, 'call_record_outgoing_external_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'call_record_outgoing_external_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'call_record_outgoing_external_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'call_record_outgoing_external_enabled', []
    yield s.check_bogus_field_returns_error, url, 'online_call_record_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'online_call_record_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'online_call_record_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'online_call_record_enabled', []
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', []
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', 'sixty'
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', -1
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', 21
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', {}
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', []
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', 'ten'
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', -1
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', 10801
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', {}
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', []
    yield s.check_bogus_field_returns_error, url, 'call_permission_password', 1234
    yield s.check_bogus_field_returns_error, url, 'call_permission_password', 'invalid_char'
    yield s.check_bogus_field_returns_error, url, 'call_permission_password', {}
    yield s.check_bogus_field_returns_error, url, 'call_permission_password', []
    yield s.check_bogus_field_returns_error, url, 'call_permission_password', s.random_string(
        17
    )
    yield s.check_bogus_field_returns_error, url, 'subscription_type', 'one'
    yield s.check_bogus_field_returns_error, url, 'subscription_type', -1
    yield s.check_bogus_field_returns_error, url, 'subscription_type', 11
    yield s.check_bogus_field_returns_error, url, 'subscription_type', {}
    yield s.check_bogus_field_returns_error, url, 'subscription_type', []
    yield s.check_bogus_field_returns_error, url, 'enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'enabled', 123
    yield s.check_bogus_field_returns_error, url, 'enabled', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', []

    conflict = {'call_record_incoming_external_enabled': True}
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', False, conflict


def put_error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'caller_id', None
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', None
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_enabled', None
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', None
    yield s.check_bogus_field_returns_error, url, 'call_record_incoming_external_enabled', None
    yield s.check_bogus_field_returns_error, url, 'call_record_incoming_internal_enabled', None
    yield s.check_bogus_field_returns_error, url, 'call_record_outgoing_internal_enabled', None
    yield s.check_bogus_field_returns_error, url, 'call_record_outgoing_external_enabled', None
    yield s.check_bogus_field_returns_error, url, 'online_call_record_enabled', None
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', None
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', None
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', None
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', None
    yield s.check_bogus_field_returns_error, url, 'enabled', None


@fixtures.user()
def test_put_errors(user):
    user_put = confd.users(user['id']).put

    for check in error_checks(user_put):
        yield check
    for check in put_error_checks(user_put):
        yield check


@fixtures.user(firstname='user1', username='unique_username', email='unique@email.com')
@fixtures.user()
def test_unique_errors(user1, user2):
    url = confd.users(user2['id']).put
    for check in unique_error_checks(url, user1):
        yield check

    required_body = {'firstname': 'user2'}
    url = confd.users.post
    for check in unique_error_checks(url, user1, required_body):
        yield check


def unique_error_checks(url, existing_resource, required_body=None):
    yield s.check_bogus_field_returns_error, url, 'username', existing_resource[
        'username'
    ], required_body
    yield s.check_bogus_field_returns_error, url, 'email', existing_resource[
        'email'
    ], required_body


def test_deprecated_call_record_enabled():
    user_args = {'firstname': 'potato', 'call_record_enabled': True}
    response = confd.users.post(user_args)
    response.assert_created('users')
    user = response.item

    confd.users(user['uuid']).put({'call_record_enabled': True})
    response = confd.users(user['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            call_record_enabled=True,
            call_record_outgoing_external_enabled=True,
            call_record_outgoing_internal_enabled=True,
            call_record_incoming_external_enabled=True,
            call_record_incoming_internal_enabled=True,
        ),
    )

    confd.users(user['uuid']).put({'call_record_enabled': False})
    response = confd.users(user['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            call_record_enabled=False,
            call_record_outgoing_external_enabled=False,
            call_record_outgoing_internal_enabled=False,
            call_record_incoming_external_enabled=False,
            call_record_incoming_internal_enabled=False,
        ),
    )

    confd.users(user['uuid']).put({'call_record_outgoing_external_enabled': True})
    response = confd.users(user['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            call_record_enabled=False,
            call_record_outgoing_external_enabled=True,
            call_record_outgoing_internal_enabled=False,
            call_record_incoming_external_enabled=False,
            call_record_incoming_internal_enabled=False,
        ),
    )

    response = confd.users(user['uuid']).delete()
    response.assert_deleted()


@fixtures.user()
def test_delete_errors(user):
    user_url = confd.users(user['id'])
    user_url.delete()
    yield s.check_resource_not_found, user_url.get, 'User'


@fixtures.user(firstname='ÉricDir')
def test_that_the_directory_view_works_with_unicode_characters(user):
    response = confd.users.get(view='directory', search='éricdir')
    response.assert_ok()

    assert_that(response.items[0]['id'], equal_to(user['id']))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_summary_view_on_sip_endpoint(user, line, sip, extension):
    with a.line_endpoint_sip(line, sip), a.line_extension(line, extension), a.user_line(
        user, line
    ):

        response = confd.users.get(view='summary', id=user['id'])
        assert_that(
            response.items,
            contains(
                has_entries(
                    id=user['id'],
                    uuid=user['uuid'],
                    firstname=user['firstname'],
                    lastname=user['lastname'],
                    email=user['email'],
                    provisioning_code=line['provisioning_code'],
                    extension=extension['exten'],
                    context=extension['context'],
                    enabled=True,
                    protocol='sip',
                )
            ),
        )


@fixtures.user()
@fixtures.line()
@fixtures.sccp()
@fixtures.extension()
def test_summary_view_on_sccp_endpoint(user, line, sccp, extension):
    with a.line_endpoint_sccp(line, sccp), a.line_extension(
        line, extension
    ), a.user_line(user, line):

        response = confd.users.get(view='summary', id=user['id'])
        assert_that(
            response.items,
            contains(
                has_entries(
                    id=user['id'],
                    uuid=user['uuid'],
                    firstname=user['firstname'],
                    lastname=user['lastname'],
                    email=user['email'],
                    provisioning_code=line['provisioning_code'],
                    extension=extension['exten'],
                    context=extension['context'],
                    enabled=True,
                    protocol='sccp',
                )
            ),
        )


@fixtures.user()
@fixtures.line()
@fixtures.custom()
@fixtures.extension()
def test_summary_view_on_custom_endpoint(user, line, custom, extension):
    with a.line_endpoint_custom(line, custom), a.line_extension(
        line, extension
    ), a.user_line(user, line):

        response = confd.users.get(view='summary', id=user['id'])
        assert_that(
            response.items,
            contains(
                has_entries(
                    id=user['id'],
                    uuid=user['uuid'],
                    firstname=user['firstname'],
                    lastname=user['lastname'],
                    email=user['email'],
                    provisioning_code=none(),
                    extension=extension['exten'],
                    context=extension['context'],
                    enabled=True,
                    protocol='custom',
                )
            ),
        )


@fixtures.user()
def test_summary_view_on_user_without_line(user):
    response = confd.users.get(view='summary', id=user['id'])
    assert_that(
        response.items,
        contains(
            has_entries(
                id=user['id'],
                uuid=user['uuid'],
                firstname=user['firstname'],
                lastname=user['lastname'],
                email=user['email'],
                provisioning_code=none(),
                extension=none(),
                context=none(),
                enabled=True,
                protocol=none(),
            )
        ),
    )


@fixtures.user(
    firstname="Léeroy",
    lastname="Jénkins",
    email="jenkins@leeroy.com",
    outgoing_caller_id='"Mystery Man" <5551234567>',
    username="leeroyjenkins",
    mobile_phone_number="5552423232",
    userfield="leeroy jenkins userfield",
    description="Léeroy Jénkin's bio",
    enabled=False,
    preprocess_subroutine="leeroy_preprocess",
)
def test_search_on_user_view(user):
    user = confd.users(user['id']).get().item
    url = confd.users
    searches = {
        'firstname': 'léeroy',
        'lastname': 'jénkins',
        'email': 'jenkins@',
        'outgoing_caller_id': '5551234567',
        'mobile_phone_number': '2423232',
        'userfield': 'jenkins userfield',
        'description': "jénkin's bio",
        'preprocess_subroutine': 'roy_preprocess',
    }

    for field, term in searches.items():
        yield check_search, url, field, term, user[field]


@fixtures.user(
    firstname="Môustapha",
    lastname="Bângoura",
    email="moustapha@bangoura.com",
    mobile_phone_number="+5559284759",
    userfield="Moustapha userfield",
    description="Moustapha the greatest dancer",
)
def test_search_on_directory_view(user):
    url = confd.users(view='directory')

    searches = {
        'firstname': 'môustapha',
        'lastname': 'bângoura',
        'email': 'moustapha@',
        'mobile_phone_number': '928475',
        'userfield': 'moustapha userfield',
        'description': "greatest dancer",
    }

    for field, term in searches.items():
        yield check_search, url, field, term, user[field]


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_search_on_users_extension(user, line, extension):
    with a.user_line(user, line), a.line_extension(line, extension):
        response = confd.users.get(search=extension['exten'], view='directory')
        assert_that(response.items, has_item(has_entry('exten', extension['exten'])))


@fixtures.user(firstname='context-filter')
@fixtures.line_sip()
@fixtures.extension()
def test_search_on_users_with_context_filter(user, line, extension):
    with a.user_line(user, line), a.line_extension(line, extension):
        response = confd.users.get(
            firstname='context-filter', view='directory', context='default'
        )
        assert_that(response.total, equal_to(1))
        assert_that(response.items, has_item(has_entry('exten', extension['exten'])))

        response = confd.users.get(
            firstname='context-filter', view='directory', context='other'
        )
        assert_that(response.total, equal_to(0))


@fixtures.user(
    firstname="Âboubacar", lastname="Manè", description="Âboubacar le grand danseur"
)
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_search_on_summary_view(user, line, sip, extension):
    url = confd.users(view='summary')

    with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(
        line, extension
    ):
        yield check_search, url, 'firstname', 'âbou', user['firstname']
        yield check_search, url, 'lastname', 'man', user['lastname']
        yield check_search, url, 'provisioning_code', line['provisioning_code'], line[
            'provisioning_code'
        ]
        yield check_search, url, 'extension', extension['exten'], extension['exten']


def check_search(url, field, term, value):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, value)))


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.users.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.users.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.users.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.user()
@fixtures.user()
@fixtures.user()
def test_list_by_multiple_uuids(_, user2, user3):
    response = confd.users.get(uuid=','.join([user2['uuid'], user3['uuid']]))
    assert_that(response.items, contains_inanyorder(user2, user3))


# TODO(pc-m): fails when running all tests
# @fixtures.user(firstname='Alice')
# @fixtures.user(firstname='Bob')
# @fixtures.user(firstname='Charles')
# def test_list_db_requests(*_):
#     s.check_db_requests(BaseIntegrationTest, confd.users.get, nb_requests=1)


@fixtures.user(
    firstname="firstname1",
    lastname="lastname1",
    email="email1@example.com",
    mobile_phone_number="+5551",
    userfield="sort userfield1",
    description="description1",
)
@fixtures.user(
    firstname="firstname2",
    lastname="lastname2",
    email="email2@example.com",
    mobile_phone_number="+5552",
    userfield="sort userfield2",
    description="description2",
)
def test_sorting_offset_limit(user1, user2):
    url = confd.users.get
    yield s.check_sorting, url, user1, user2, 'firstname', 'firstname'
    yield s.check_sorting, url, user1, user2, 'lastname', 'lastname'
    yield s.check_sorting, url, user1, user2, 'email', 'email'
    yield s.check_sorting, url, user1, user2, 'mobile_phone_number', '+555'
    yield s.check_sorting, url, user1, user2, 'userfield', 'sort userfield'
    yield s.check_sorting, url, user1, user2, 'description', 'description'

    yield s.check_offset, url, user1, user2, 'firstname', 'firstname'
    yield s.check_limit, url, user1, user2, 'firstname', 'firstname'


@fixtures.user()
def test_head(user):
    response = confd.users(user['uuid']).head()
    response.assert_ok()


@fixtures.user(**FULL_USER)
def test_get(user):
    response = confd.users(user['id']).get()
    assert_that(response.item, has_entries(FULL_USER))
    assert_that(
        response.item,
        has_entries(
            agent=none(),
            call_permissions=empty(),
            incalls=empty(),
            lines=empty(),
            groups=empty(),
            forwards={
                'busy': {'destination': None, 'enabled': False},
                'noanswer': {'destination': None, 'enabled': False},
                'unconditional': {'destination': None, 'enabled': False},
            },
            services={'dnd': {'enabled': False}, 'incallfilter': {'enabled': False}},
            voicemail=none(),
            queues=empty(),
            call_pickup_target_users=empty(),
        ),
    )


@fixtures.user(firstname="Snôm", lastname="Whîte")
@fixtures.user()
@fixtures.user()
def test_that_get_by_uuid(user_1, user_2_, user_3):
    result = confd.users(user_1['uuid']).get()

    assert_that(result.item, has_entries(firstname='Snôm', lastname='Whîte'))


@fixtures.user(
    firstname="Snôw", lastname="Whîte", username='snow.white+dwarves@disney.example.com'
)
def test_that_the_username_can_be_an_email(user):
    result = confd.users(user['id']).get()

    assert_that(
        result.item,
        has_entries(
            firstname='Snôw',
            lastname='Whîte',
            username='snow.white+dwarves@disney.example.com',
        ),
    )


def test_create_minimal_parameters():
    response = confd.users.post(firstname="Roger")

    response.assert_created('users')
    assert_that(response.item, has_entry("firstname", "Roger"))


def test_create_with_null_parameters_fills_default_values():
    response = confd.users.post(firstname="Charlie")
    response.assert_created('users')

    assert_that(
        response.item,
        has_entries(
            caller_id='"Charlie"',
            call_transfer_enabled=False,
            dtmf_hangup_enabled=False,
            call_record_outgoing_external_enabled=False,
            call_record_outgoing_internal_enabled=False,
            call_record_incoming_external_enabled=False,
            call_record_incoming_internal_enabled=False,
            online_call_record_enabled=False,
            supervision_enabled=True,
            ring_seconds=30,
            simultaneous_calls=5,
        ),
    )


def test_create_with_all_parameters():
    response = confd.users.post(**FULL_USER)

    response.assert_created('users')
    try:
        assert_that(response.item, has_entries(FULL_USER))
        assert_that(response.item, has_entries(created_at=is_not(none())))
    finally:
        confd.users(response.item['uuid']).delete().assert_deleted()


def test_create_with_voicemail_relation():
    vm_number = h.voicemail.find_available_number(CONTEXT)
    voicemail = {
        'name': 'full',
        'number': vm_number,
        'context': CONTEXT,
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

    response = confd.users.post(
        {
            'voicemail': voicemail,
            **FULL_USER,
        }
    )
    user_uuid = response.item['uuid']

    response.assert_created()
    try:
        assert_that(
            confd.users(user_uuid).get().item,
            has_entries(
                voicemail=has_entries(id=greater_than(0)),
            ),
        )
        voicemail_id = response.item['voicemail']['id']
        assert_that(
            response.item,
            has_entries(
                voicemail=has_entries(
                    id=greater_than(0),
                )
            ),
        )
    finally:
        confd.users(user_uuid).voicemails.delete().assert_deleted()
        confd.voicemails(voicemail_id).delete().assert_deleted()
        confd.users(user_uuid).delete().assert_deleted()


@fixtures.voicemail()
def test_post_full_user_existing_voicemail(voicemail):
    response = confd.users.post(
        {
            'voicemail': {'id': voicemail['id']},
            **FULL_USER,
        }
    )

    response.assert_created()
    user_uuid = response.item['uuid']
    try:
        assert_that(
            response.item,
            has_entries(
                voicemail=has_entries(
                    id=voicemail['id'],
                )
            ),
        )

        assert_that(
            confd.users(user_uuid).get().item,
            has_entries(
                voicemail=has_entries(
                    id=voicemail['id'],
                )
            ),
        )
    finally:
        confd.users(user_uuid).voicemails.delete().assert_deleted()
        confd.users(user_uuid).delete().assert_deleted()


def test_create_with_all_parameters_null():
    response = confd.users.post(**NULL_USER)
    assert_that(response.item, has_entries(NULL_USER))


def test_create_generates_appropriate_caller_id():
    response = confd.users.post(firstname='Jôhn')
    assert_that(response.item, has_entry('caller_id', '"Jôhn"'))

    response = confd.users.post(firstname='Jôhn', lastname='Doe')
    assert_that(response.item['caller_id'], equal_to('"Jôhn Doe"'))


@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_create_multi_tenant_moh(main_moh, sub_moh):
    parameters = {
        'firstname': 'MyUser',
        'music_on_hold': main_moh['name'],
    }
    response = confd.users.post(**parameters)
    response.assert_created('users')
    confd.users(response.item['id']).delete().assert_deleted()

    response = confd.users.post(**parameters, wazo_tenant=SUB_TENANT)
    response.assert_match(400, e.not_found(resource='MOH'))

    parameters['music_on_hold'] = sub_moh['name']

    response = confd.users.post(**parameters, wazo_tenant=SUB_TENANT)
    response.assert_created('users')
    confd.users(response.item['id']).delete().assert_deleted()

    response = confd.users.post(**parameters)
    response.assert_match(400, e.not_found(resource='MOH'))


@fixtures.transport()
@fixtures.sip_template()
@fixtures.registrar()
def test_post_full_user_no_error(transport, template, registrar):
    exten = h.extension.find_available_exten(CONTEXT)
    user = {
        "subscription_type": 2,
        "firstname": "Rîchard",
        "lastname": "Lâpointe",
        "email": "richard@lapointe.org",
        "language": "fr_FR",
        "outgoing_caller_id": '"Rîchy Cool" <4185551234>',
        "mobile_phone_number": "4181234567",
        "supervision_enabled": True,
        "call_transfer_enabled": False,
        "dtmf_hangup_enabled": True,
        "call_record_outgoing_external_enabled": True,
        "call_record_outgoing_internal_enabled": True,
        "call_record_incoming_internal_enabled": True,
        "call_record_incoming_external_enabled": True,
        "online_call_record_enabled": False,
        "simultaneous_calls": 5,
        "ring_seconds": 30,
        "userfield": "userfield",
        "call_permission_password": "1234",
        "enabled": True,
        "username": "richardlapointe",
        "password": "secret",
    }
    extension = {'context': CONTEXT, 'exten': exten}
    line = {
        'context': CONTEXT,
        'position': 2,
        'registrar': registrar['id'],
        'provisioning_code': "887865",
        'extensions': [extension],
        'endpoint_sip': {
            'name': 'iddqd',
            'label': 'Richard\'s line',
            'auth_section_options': [
                ['username', 'iddqd'],
                ['password', 'secret'],
            ],
            'endpoint_section_options': [
                ['callerid', f'"Rîchard Lâpointe" <{exten}>'],
            ],
            'transport': transport,
            'templates': [template],
        },
    }

    response = confd.users.post(
        {
            'lines': [line],
            **user,
        }
    ).response

    assert response.status_code == 201
    payload = response.json()
    try:
        assert_that(
            payload,
            has_entries(
                uuid=uuid_(),
                lines=contains(
                    has_entries(
                        id=greater_than(0),
                        endpoint_sip=has_entries(uuid=uuid_()),
                        extensions=contains(has_entries(id=greater_than(0))),
                    )
                ),
                **user,
            ),
        )

        assert_that(
            confd.users(payload['uuid']).get().item,
            has_entries(lines=contains(has_entries(id=payload['lines'][0]['id']))),
        )

        assert_that(
            confd.lines(payload['lines'][0]['id']).get().item,
            has_entries(
                extensions=contains(has_entries(**extension)),
                endpoint_sip=has_entries(name='iddqd'),
            ),
        )

        user = confd.users(payload['uuid']).get().item
        user.pop('call_record_enabled', None)  # Deprecated field
        confd.users(payload['uuid']).put(**user).assert_updated()
    finally:
        confd.users(payload['uuid']).delete().assert_deleted()
        confd.lines(payload['lines'][0]['id']).delete().assert_deleted()
        confd.extensions(
            payload['lines'][0]['extensions'][0]['id']
        ).delete().assert_deleted()


@fixtures.user(
    firstname="Léeroy",
    lastname="Jénkins",
    email="leeroy@jenkins.com",
    outgoing_caller_id='"Mystery Man" <5551234567>',
    username="leeroyjenkins",
    music_on_hold="",
    mobile_phone_number="5552423232",
    userfield="leeroy jenkins userfield",
    description="Léeroy Jénkin's bio",
    preprocess_subroutine="leeroy_preprocess",
)
def test_update_with_all_parameters(user):
    user_url = confd.users(user['id'])

    response = user_url.put(**FULL_USER)
    response.assert_updated()

    response = user_url.get()
    assert_that(response.item, has_entries(FULL_USER))


@fixtures.user()
def test_update_with_all_parameters_null(user):
    response = confd.users(user['id']).put(**NULL_USER)
    response.assert_updated()

    response = confd.users(user['id']).get()
    assert_that(response.item, has_entries(**NULL_USER))


@fixtures.user()
def test_update_by_uuid(user):
    response = confd.users(user['uuid']).put({'firstname': 'Fôo', 'lastname': 'Bâr'})
    response.assert_updated()

    response = confd.users(user['uuid']).get()
    assert_that(response.item, has_entries(firstname='Fôo', lastname='Bâr'))


@fixtures.user(firstname='main', wazo_tenant=MAIN_TENANT)
@fixtures.user(firstname='sub', wazo_tenant=SUB_TENANT)
@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant_moh(main, sub, main_moh, sub_moh):
    response = confd.users(main['id']).put(music_on_hold=sub_moh['name'])
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.users(sub['id']).put(music_on_hold=main_moh['name'])
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.users(main['id']).put(music_on_hold=main_moh['name'])
    response.assert_updated()

    response = confd.users(sub['id']).put(music_on_hold=sub_moh['name'])
    response.assert_updated()


@fixtures.user()
def test_delete(user):
    response = confd.users(user['id']).delete()
    response.assert_deleted()


@fixtures.user()
def test_delete_by_uuid(user):
    response = confd.users(user['uuid']).delete()
    response.assert_deleted()

    response = confd.users(user['uuid']).get()
    response.assert_status(404)


@fixtures.user()
def test_bus_events(user):
    url = confd.users(user['id'])
    body = {'firstname': 'test-event-user'}
    headers = {'tenant_uuid': user['tenant_uuid']}

    yield s.check_event, 'user_created', headers, confd.users.post, body
    yield s.check_event, 'user_edited', headers, url.put
    yield s.check_event, 'user_deleted', headers, url.delete


def generate_user_resources_bodies(group, switchboard):
    exten = h.extension.find_available_exten(CONTEXT)
    source_exten = h.extension.find_available_exten(INCALL_CONTEXT)
    user = FULL_USER
    auth = AUTH_USER
    extension = {'context': CONTEXT, 'exten': exten}
    line = {
        'context': CONTEXT,
        'extensions': [extension],
        'endpoint_sip': {'name': 'iddqd'},
    }
    incall = {
        'extensions': [{'context': INCALL_CONTEXT, 'exten': source_exten}],
    }
    group = {
        'uuid': group['uuid'],
    }
    switchboard = {
        'uuid': switchboard['uuid'],
    }
    return exten, source_exten, user, auth, extension, line, incall, group, switchboard


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}}
)
@fixtures.switchboard()
def test_post_full_user_no_error(
    group_extension,
    group,
    funckey_template,
    switchboard,
):
    (
        exten,
        source_exten,
        user,
        auth,
        extension,
        line,
        incall,
        group,
        switchboard,
    ) = generate_user_resources_bodies(group, switchboard)

    with a.group_extension(group, group_extension):
        response = confd.users.post(
            {
                'auth': auth,
                'lines': [line],
                'incalls': [incall],
                'groups': [group],
                'func_key_template_id': funckey_template['id'],
                'switchboards': [switchboard],
                **user,
            }
        )

        response.assert_created('users')
        payload = response.item

        try:
            # check the data returned when the user is created
            assert_that(
                payload,
                has_entries(
                    uuid=uuid_(),
                    lines=contains(
                        has_entries(
                            id=greater_than(0),
                            endpoint_sip=has_entries(uuid=uuid_()),
                            extensions=contains(has_entries(id=greater_than(0))),
                        )
                    ),
                    incalls=contains(
                        has_entries(
                            id=greater_than(0),
                            extensions=contains(
                                has_entries(
                                    id=greater_than(0),
                                    context=INCALL_CONTEXT,
                                    exten=source_exten,
                                )
                            ),
                        )
                    ),
                    groups=contains(
                        has_entries(uuid=group['uuid']),
                    ),
                    func_key_template_id=funckey_template['id'],
                    switchboards=contains(
                        has_entries(uuid=switchboard['uuid']),
                    ),
                    auth=has_entries(
                        uuid=payload['uuid'],
                        firstname=user['firstname'],
                        lastname=user['lastname'],
                        emails=contains(has_entries(address=user['email'])),
                        username=auth['username'],
                    ),
                    **user,
                ),
            )

            # retrieve the user (created before) and check their fields
            assert_that(
                confd.users(payload['uuid']).get().item,
                has_entries(
                    lines=contains(has_entries(id=payload['lines'][0]['id'])),
                    incalls=contains(has_entries(id=payload['incalls'][0]['id'])),
                    groups=contains(has_entries(uuid=payload['groups'][0]['uuid'])),
                    switchboards=contains(
                        has_entries(uuid=payload['switchboards'][0]['uuid'])
                    ),
                ),
            )
            # retrieve the line (created before) and check its data are correct
            assert_that(
                confd.lines(payload['lines'][0]['id']).get().item,
                has_entries(
                    extensions=contains(has_entries(**extension)),
                    endpoint_sip=has_entries(name='iddqd'),
                ),
            )
            # retrieve the incall (created before) and check its data are correct
            assert_that(
                confd.incalls(payload['incalls'][0]['id']).get().item,
                has_entries(
                    destination=has_entries(type="user", user_id=payload['id'])
                ),
            )
            # retrieve the group and check the user is a member
            assert_that(
                confd.groups(payload['groups'][0]['uuid']).get().item,
                has_entries(
                    members=has_entries(
                        users=contains(has_entries(uuid=payload['uuid']))
                    )
                ),
            )
            # retrieve the switchboard and check the user is a member
            assert_that(
                confd.switchboards(payload['switchboards'][0]['uuid']).get().item,
                has_entries(
                    members=has_entries(
                        users=contains(has_entries(uuid=payload['uuid']))
                    )
                ),
            )
            # retrieve the user (created before) and check their func keys template
            assert_that(
                confd.users(payload['uuid']).get().item,
                has_entries(func_key_template_id=payload['func_key_template_id']),
            )
            # check if auth user exists
            wazo_user = authentication.users.get(payload['uuid'])
            assert_that(
                wazo_user,
                has_entries(
                    uuid=payload['uuid'],
                    username=auth['username'],
                ),
            )
            # retrieve the user and try to update the user with the same data
            user = confd.users(payload['uuid']).get().item
            user.pop('call_record_enabled', None)  # Deprecated field
            user.pop(
                'voicemail', None
            )  # The voicemail cannot be updated directly by calling POST /users
            confd.users(payload['uuid']).put(**user).assert_updated()

            wazo_user = authentication.users.get(payload['uuid'])
            assert_that(
                wazo_user,
                has_entries(
                    uuid=payload['uuid'],
                    firstname=user['firstname'],
                    lastname=user['lastname'],
                    emails=contains(has_entries(address=user['email'])),
                    username=auth['username'],
                ),
            )

        finally:
            confd.users(payload['uuid']).delete().assert_deleted()
            confd.lines(payload['lines'][0]['id']).delete().assert_deleted()
            confd.incalls(payload['incalls'][0]['id']).delete().assert_deleted()
            confd.extensions(
                payload['lines'][0]['extensions'][0]['id']
            ).delete().assert_deleted()
            authentication.users.delete(payload['uuid'])


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}}
)
@fixtures.switchboard()
def test_delete_full_user_no_error(
    group_extension,
    group,
    funckey_template,
    switchboard,
):
    (
        exten,
        source_exten,
        user,
        auth,
        extension,
        line,
        incall,
        group,
        switchboard,
    ) = generate_user_resources_bodies(group, switchboard)

    with a.group_extension(group, group_extension):

        response = confd.users.post(
            {
                'auth': auth,
                'lines': [line],
                'incalls': [incall],
                'groups': [group],
                'func_key_template_id': funckey_template['id'],
                'switchboards': [switchboard],
                **user,
            }
        )

        payload = response.json

        # user deletion
        url = confd.users(payload['uuid'])

        response = url.delete(recursive=True)
        response.assert_deleted()

        # verify that user is deleted
        response = url.get()
        response.assert_status(404)

        # verify that line is deleted
        url = confd.lines(payload['lines'][0]['id'])
        response = url.get()
        response.assert_status(404)

        # verify that incall is deleted
        url = confd.incalls(payload['incalls'][0]['id'])
        response = url.get()
        response.assert_status(404)

        # verify that extension is deleted
        url = confd.extensions(payload['lines'][0]['extensions'][0]['id'])
        response = url.get()
        response.assert_status(404)

        # verify that the switchboard is not deleted
        url = confd.switchboards(payload['switchboards'][0]['uuid'])
        response = url.get()
        response.assert_ok()

        # verify that the group is not deleted
        url = confd.groups(payload['groups'][0]['uuid'])
        response = url.get()
        response.assert_ok()

        # verify auth user is deleted
        assert_that(
            calling(authentication.users.get).with_args(payload['uuid']),
            raises(HTTPError, "404 Client Error: NOT FOUND"),
        )


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}}
)
@fixtures.switchboard()
def test_delete_full_user_no_auth_no_error(
    group_extension,
    group,
    funckey_template,
    switchboard,
):
    (
        exten,
        source_exten,
        user,
        auth,
        extension,
        line,
        incall,
        group,
        switchboard,
    ) = generate_user_resources_bodies(group, switchboard)

    with a.group_extension(group, group_extension):

        response = confd.users.post(
            {
                'lines': [line],
                'incalls': [incall],
                'groups': [group],
                'func_key_template_id': funckey_template['id'],
                'switchboards': [switchboard],
                **user,
            }
        )

        payload = response.json

        # user deletion
        url = confd.users(payload['uuid'])
        url.delete(recursive=True)

        # verify auth user is deleted
        assert_that(
            calling(authentication.users.get).with_args(payload['uuid']),
            raises(HTTPError, "404 Client Error: NOT FOUND"),
        )


@fixtures.user()
def test_delete_simple_user_with_recursive_true(user):
    response = confd.users(user['uuid']).delete(recursive=True)
    response.assert_deleted()

    response = confd.users(user['uuid']).get()
    response.assert_status(404)
