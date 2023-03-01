# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
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
    starts_with,
)
from wazo_test_helpers.hamcrest.uuid_ import uuid_

from . import confd, provd, auth as authentication
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
    helpers as h,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
    gen_group_exten,
    CONTEXT,
    INCALL_CONTEXT,
    OUTCALL_CONTEXT,
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


class UserResources:
    def __init__(
        self,
        exten,
        source_exten,
        user,
        auth,
        extension,
        line,
        incall,
        group,
        switchboard,
        voicemail,
        forwards,
        fallbacks,
        agent,
    ):
        self.exten = exten
        self.source_exten = source_exten
        self.user = user
        self.auth = auth
        self.extension = extension
        self.line = line
        self.incall = incall
        self.group = group
        self.switchboard = switchboard
        self.voicemail = voicemail
        self.forwards = forwards
        self.fallbacks = fallbacks
        self.agent = agent


def generate_user_resources_bodies(
    group=None,
    switchboard=None,
    context_name=None,
    incall_context_name=None,
    device=None,
    user_destination=None,
    queue=None,
    endpoint_name=None,
) -> UserResources:
    exten = h.extension.find_available_exten(context_name)
    vm_number = h.voicemail.find_available_number(context_name)
    if incall_context_name:
        source_exten = h.extension.find_available_exten(incall_context_name)
    else:
        source_exten = None
    user = FULL_USER
    auth = AUTH_USER
    extension = {'context': context_name, 'exten': exten}
    if not endpoint_name:
        endpoint_name = s.random_string(5)

    line = {
        'context': context_name,
        'extensions': [extension],
        'endpoint_sip': {'name': endpoint_name},
    }
    if device:
        line['device_id'] = device['id']
    if incall_context_name:
        incall = {
            'extensions': [{'context': incall_context_name, 'exten': source_exten}],
        }
    else:
        incall = None
    if group:
        group = {
            'uuid': group['uuid'],
        }
    if switchboard:
        switchboard = {
            'uuid': switchboard['uuid'],
        }
    voicemail = {
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
    if user_destination:
        forwards = {
            'busy': {'enabled': True, 'destination': '123'},
            'noanswer': {'enabled': True, 'destination': '456'},
            'unconditional': {'enabled': True, 'destination': '789'},
        }
        fallbacks = {
            'noanswer_destination': {'type': 'user', 'user_id': user_destination['id']},
            'busy_destination': {'type': 'user', 'user_id': user_destination['id']},
            'congestion_destination': {
                'type': 'user',
                'user_id': user_destination['id'],
            },
            'fail_destination': {'type': 'user', 'user_id': user_destination['id']},
        }
    else:
        forwards = None
        fallbacks = None
    agent = {}
    if queue:
        agent['queues'] = [{'id': queue['id'], 'penalty': 1, 'priority': 2}]
    return UserResources(
        exten,
        source_exten,
        user,
        auth,
        extension,
        line,
        incall,
        group,
        switchboard,
        voicemail,
        forwards,
        fallbacks,
        agent,
    )


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}}
)
@fixtures.switchboard()
@fixtures.device()
@fixtures.user()
@fixtures.switchboard()
@fixtures.user()
@fixtures.queue()
@fixtures.group()
def test_post_update_delete_full_user_no_error(
    group_extension,
    group,
    funckey_template,
    switchboard,
    device,
    user_destination,
    switchboard2,
    user2,
    queue,
    new_group,
):
    user_resources = generate_user_resources_bodies(
        group=group,
        switchboard=switchboard,
        context_name=CONTEXT,
        incall_context_name=INCALL_CONTEXT,
        device=device,
        user_destination=user_destination,
        queue=queue,
    )

    with a.switchboard_member_user(switchboard2, [user2]):
        with a.group_extension(group, group_extension):
            user_body = {
                'auth': user_resources.auth,
                'lines': [user_resources.line],
                'incalls': [user_resources.incall],
                'groups': [group],
                'func_key_template_id': funckey_template['id'],
                'switchboards': [switchboard, switchboard2],
                'agent': user_resources.agent,
                'voicemail': user_resources.voicemail,
                'forwards': user_resources.forwards,
                'fallbacks': user_resources.fallbacks,
                **user_resources.user,
            }
            response = confd.users.post(user_body)

            response.assert_created('users')
            payload = response.item

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
                            device_id=device['id'],
                        )
                    ),
                    incalls=contains(
                        has_entries(
                            id=greater_than(0),
                            extensions=contains(
                                has_entries(
                                    id=greater_than(0),
                                    context=INCALL_CONTEXT,
                                    exten=user_resources.source_exten,
                                )
                            ),
                        )
                    ),
                    groups=contains(
                        has_entries(uuid=group['uuid']),
                    ),
                    func_key_template_id=funckey_template['id'],
                    switchboards=contains_inanyorder(
                        has_entries(uuid=switchboard['uuid']),
                        has_entries(uuid=switchboard2['uuid']),
                    ),
                    auth=has_entries(
                        uuid=payload['uuid'],
                        firstname=user_resources.user['firstname'],
                        lastname=user_resources.user['lastname'],
                        emails=contains(
                            has_entries(address=user_resources.user['email'])
                        ),
                        username=user_resources.auth['username'],
                    ),
                    agent=has_entries(
                        number=user_resources.line['extensions'][0]['exten'],
                        firstname=user_resources.user['firstname'],
                        queues=contains(
                            has_entries(
                                id=user_resources.agent['queues'][0]['id'],
                                penalty=user_resources.agent['queues'][0]['penalty'],
                                priority=user_resources.agent['queues'][0]['priority'],
                            )
                        ),
                    ),
                    voicemail=has_entries(id=greater_than(0)),
                    forwards=has_entries(**user_resources.forwards),
                    fallbacks=has_entries(
                        noanswer_destination=has_entries(
                            type='user', user_id=user_destination['id']
                        ),
                        busy_destination=has_entries(
                            type='user', user_id=user_destination['id']
                        ),
                        congestion_destination=has_entries(
                            type='user', user_id=user_destination['id']
                        ),
                        fail_destination=has_entries(
                            type='user', user_id=user_destination['id']
                        ),
                    ),
                    **user_resources.user,
                ),
            )

            # retrieve the user (created before) and check their fields
            assert_that(
                confd.users(payload['uuid']).get().item,
                has_entries(
                    lines=contains(has_entries(id=payload['lines'][0]['id'])),
                    incalls=contains(has_entries(id=payload['incalls'][0]['id'])),
                    groups=contains(has_entries(uuid=payload['groups'][0]['uuid'])),
                    switchboards=contains_inanyorder(
                        has_entries(uuid=payload['switchboards'][0]['uuid']),
                        has_entries(uuid=switchboard2['uuid']),
                    ),
                ),
            )
            # retrieve the line (created before) and check its data are correct
            assert_that(
                confd.lines(payload['lines'][0]['id']).get().item,
                has_entries(
                    extensions=contains(has_entries(**user_resources.extension)),
                    endpoint_sip=has_entries(
                        name=user_resources.line['endpoint_sip']['name']
                    ),
                    device_id=device['id'],
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
            # retrieve the switchboard2 and check the user is a member
            assert_that(
                confd.switchboards(switchboard2['uuid']).get().item,
                has_entries(
                    members=has_entries(
                        users=contains_inanyorder(
                            has_entries(uuid=user2['uuid']),
                            has_entries(uuid=payload['uuid']),
                        )
                    )
                ),
            )
            # retrieve the forwards for the user and check the data
            assert_that(
                confd.users(payload['uuid']).forwards.get().item,
                has_entries(**user_resources.forwards),
            )
            # retrieve the fallbacks for the user and check the data
            assert_that(
                confd.users(payload['uuid']).fallbacks.get().item,
                has_entries(
                    noanswer_destination=has_entries(
                        type='user', user_id=user_destination['id']
                    ),
                    busy_destination=has_entries(
                        type='user', user_id=user_destination['id']
                    ),
                    congestion_destination=has_entries(
                        type='user', user_id=user_destination['id']
                    ),
                    fail_destination=has_entries(
                        type='user', user_id=user_destination['id']
                    ),
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
                    username=user_resources.auth['username'],
                ),
            )
            # retrieve the agent for the user and check the data
            assert_that(
                confd.agents(payload['agent']['id']).get().item,
                has_entries(
                    number=user_resources.line['extensions'][0]['exten'],
                    firstname=user_resources.user['firstname'],
                    queues=contains(has_entries(id=queue['id'])),
                ),
            )
            # retrieve the voicemail (created before) and check its data are correct
            assert_that(
                confd.voicemails(payload['voicemail']['id']).get().item,
                has_entries(
                    name=f"{user_resources.user['firstname']} {user_resources.user['lastname']}",
                    id=payload['voicemail']['id'],
                ),
            )
            # retrieve the user and try to update the user with the same data
            user = confd.users(payload['uuid']).get().item
            user.pop('call_record_enabled', None)  # Deprecated field
            user.pop(
                'voicemail', None
            )  # The voicemail cannot be updated directly by calling POST /users
            confd.users(payload['uuid']).put(
                **user,
                query_string="recursive=True",
            ).assert_updated()

            url = confd.users(payload['uuid'])

            # user update
            destination = {
                'type': 'voicemail',
                'voicemail_id': payload['voicemail']['id'],
            }
            new_fallbacks = {
                'noanswer_destination': destination,
                'busy_destination': destination,
                'congestion_destination': destination,
                'fail_destination': destination,
            }
            new_forwards = {
                'busy': {'enabled': True, 'destination': '456'},
                'noanswer': {'enabled': True, 'destination': '789'},
                'unconditional': {'enabled': True, 'destination': '101'},
            }
            agent_language = 'es_ES'

            payload.pop('call_record_enabled', None)  # Deprecated field
            payload['lines'][0].pop('caller_id', None)  # cannot set caller id to none
            payload['lines'][0].pop(
                'caller_id_name', None
            )  # cannot set caller id to none
            payload['lines'][0].pop(
                'caller_id_num', None
            )  # cannot set caller id to none

            response = url.put(
                {
                    **payload,
                    'fallbacks': {**new_fallbacks},
                    'forwards': {**new_forwards},
                    'groups': [{'uuid': new_group['uuid']}],
                    'agent': {'id': payload['agent']['id'], 'language': agent_language},
                },
                query_string="recursive=True",
            )
            response.assert_updated()

            # retrieve the fallbacks for the user and check the data
            assert_that(
                confd.users(payload['uuid']).fallbacks.get().item,
                has_entries(
                    noanswer_destination=has_entries(**destination),
                    busy_destination=has_entries(**destination),
                    congestion_destination=has_entries(**destination),
                    fail_destination=has_entries(**destination),
                ),
            )

            # retrieve the forwards for the user and check the data
            assert_that(
                confd.users(payload['uuid']).forwards.get().item,
                has_entries(**new_forwards),
            )

            # retrieve the groups for the user and check the data
            assert_that(
                confd.groups(new_group['uuid']).get().item,
                has_entries(
                    members=has_entries(
                        users=contains(has_entries(uuid=payload['uuid']))
                    )
                ),
            )

            # retrieve the data for the user and check the data returned (fallbacks, forwards and groups)
            assert_that(
                confd.users(payload['uuid']).get().item,
                has_entries(
                    fallbacks=has_entries(
                        noanswer_destination=has_entries(**destination),
                        busy_destination=has_entries(**destination),
                        congestion_destination=has_entries(**destination),
                        fail_destination=has_entries(**destination),
                    ),
                    forwards=has_entries(**new_forwards),
                    groups=contains(
                        has_entries(
                            id=new_group['id'],
                            uuid=new_group['uuid'],
                            name=new_group['name'],
                        )
                    ),
                ),
            )

            # retrieve the agent for the user and check the data
            response = url.get()
            payload = response.item
            assert_that(
                confd.agents(payload['agent']['id']).get().item,
                has_entries(
                    language=agent_language,
                    firstname=user['firstname'],
                ),
            )

            # user deletion
            response = url.delete(recursive=True)
            response.assert_deleted()

            # verify that user is deleted
            response = url.get()
            response.assert_status(404)

            # verify that voicemail is deleted
            url = confd.lines(payload['voicemail']['id'])
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

            # verify that the switchboard2 is not deleted
            url = confd.switchboards(switchboard2['uuid'])
            response = url.get()
            response.assert_ok()

            # verify that the group is not deleted
            url = confd.groups(payload['groups'][0]['uuid'])
            response = url.get()
            response.assert_ok()

            # verify that auth user is deleted
            assert_that(
                calling(authentication.users.get).with_args(payload['uuid']),
                raises(HTTPError, "404 Client Error: NOT FOUND"),
            )

            # verify that the device is not deleted
            url = confd.devices(device['id'])
            response = url.get()
            response.assert_ok()

            # verify that agent is deleted
            url = confd.agents(payload['agent']['id'])
            response = url.get()
            response.assert_status(404)


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
    user_resources = generate_user_resources_bodies(
        group=group,
        switchboard=switchboard,
        context_name=CONTEXT,
        incall_context_name=INCALL_CONTEXT,
    )

    with a.group_extension(group, group_extension):
        response = confd.users.post(
            {
                'lines': [user_resources.line],
                'incalls': [user_resources.incall],
                'groups': [group],
                'func_key_template_id': funckey_template['id'],
                'switchboards': [switchboard],
                **user_resources.user,
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

    # check that the user does not exist anymore
    response = confd.users(user['uuid']).get()
    response.assert_status(404)


@fixtures.device(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT, name='default2')
def test_post_delete_minimalistic_user_with_unallocated_device_no_error(
    device, context
):
    user_resources = generate_user_resources_bodies(
        context_name=context['name'], device=device
    )

    response = confd.users.post(
        {
            'lines': [user_resources.line],
            **user_resources.user,
        },
        wazo_tenant=SUB_TENANT,
    )

    response.assert_created('users')
    payload = response.item

    # check if the returned data contains the device_id
    assert_that(
        payload,
        has_entries(
            uuid=uuid_(),
            lines=contains(
                has_entries(
                    device_id=device['id'],
                )
            ),
            **user_resources.user,
        ),
    )

    # retrieve the line (created before) and check if the device is associated to the line
    assert_that(
        confd.lines(payload['lines'][0]['id']).get().item,
        has_entries(device_id=device['id']),
    )

    # retrieve the device (created as an unallocated device) and check if its tenant is
    # now the user tenant
    assert_that(
        confd.devices(device['id']).get().item,
        has_entries(tenant_uuid=SUB_TENANT),
    )

    # user deletion
    response = confd.users(response.item['uuid']).delete(recursive=True)
    response.assert_deleted()

    # retrieve the device (previously created as an unallocated device)
    # and check if its tenant is always the user tenant and if status=autoprov
    device_cfg = provd.devices.get(device['id'])
    assert_that(
        device_cfg, has_entries(config=starts_with('autoprov'), tenant_uuid=SUB_TENANT)
    )


def test_post_delete_minimalistic_user_with_non_existing_device_id_error():
    user_resources = generate_user_resources_bodies(
        context_name=CONTEXT, device={'id': 'my_device'}
    )

    response = confd.users.post(
        {
            'lines': [user_resources.line],
            **user_resources.user,
        },
    )

    response.assert_status(404)
    assert_that(
        response.raw,
        equal_to(
            '["Resource Not Found - Device was not found (\'id\': \'my_device\')"]\n'
        ),
    )


@fixtures.extension(exten=gen_group_exten())
@fixtures.user()
@fixtures.voicemail()
def test_delete_voicemail_2_users_not_deleted(
    group_extension,
    user2,
    voicemail2,
):
    user_resources = generate_user_resources_bodies()

    with a.user_voicemail(user2, voicemail2, check=False):
        response = confd.users.post(
            {
                'voicemail': {**voicemail2},
                **user_resources.user,
            }
        )

        payload = response.item

        url = confd.users(payload['uuid'])

        # user deletion
        response = url.delete(recursive=True)
        response.assert_deleted()

        # verify that user is deleted
        response = url.get()
        response.assert_status(404)

        # verify that voicemail is not deleted because user2 uses the same voicemail
        url = confd.voicemails(payload['voicemail']['id'])
        response = url.get()
        response.assert_ok()


@fixtures.incall(wazo_tenant=MAIN_TENANT)
@fixtures.extension(context=INCALL_CONTEXT)
def test_post_incalls_existing_extension_no_error(incall, extension):
    incalls_list = [
        [
            {
                'extensions': [{'id': extension['id']}],
            }
        ],
        [
            {
                'extensions': [
                    {'context': extension['context'], 'exten': extension['exten']}
                ],
            }
        ],
    ]

    for incalls_elt in incalls_list:
        with a.incall_extension(incall, extension):
            user = FULL_USER
            user_body = {
                'incalls': incalls_elt,
                **user,
            }
            response = confd.users.post(user_body)

            response.assert_created('users')
            payload = response.item

            # retrieve the incall (created before) and check its data are correct
            assert_that(
                confd.incalls(payload['incalls'][0]['id']).get().item,
                has_entries(
                    destination=has_entries(type="user", user_id=payload['id'])
                ),
            )
        # user deletion
        url = confd.users(payload['uuid'])
        url.delete()


@fixtures.incall()
@fixtures.context(
    name='test-context',
    label='test-context',
    type='incall',
    description='test-context',
    incall_ranges=[],
)
@fixtures.extension(context='test-context')
def test_post_incalls_existing_extension_missing_range_no_error(
    incall, context, extension
):
    with a.incall_extension(incall, extension):
        user = FULL_USER
        user_body = {
            'incalls': [
                {
                    'extensions': [{'id': extension['id']}],
                }
            ],
            **user,
        }
        response = confd.users.post(user_body)

        response.assert_created('users')
        payload = response.item

        # retrieve the context and check if the incall range has been added
        assert_that(
            confd.contexts(context['id']).get().item,
            has_entries(
                incall_ranges=contains(
                    has_entries(
                        start=extension['exten'],
                        end=extension['exten'],
                        did_length=len(extension['exten']),
                    )
                )
            ),
        )
    # user deletion
    url = confd.users(payload['uuid'])
    url.delete(recursive=True)


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_post_incalls_existing_extension_wrong_context_type_error(outcall, extension):
    with a.outcall_extension(outcall, extension):
        user = FULL_USER
        user_body = {
            'incalls': [
                {
                    'extensions': [{'id': extension['id']}],
                }
            ],
            **user,
        }
        response = confd.users.post(user_body)

        response.assert_status(400)
        assert_that(
            response.raw,
            equal_to(
                '["Context associated to the extension is not of type \'incall\'"]\n'
            ),
        )


@fixtures.device()
@fixtures.device()
def test_update_lines_no_error(device, new_device):
    user_resources = generate_user_resources_bodies(
        context_name=CONTEXT, device=device, endpoint_name='abc'
    )

    user_body = {
        'lines': [user_resources.line],
        **user_resources.user,
    }
    response = confd.users.post(user_body)

    response.assert_created('users')
    payload = response.item

    first_line_id = confd.users(payload['uuid']).get().item['lines'][0]['id']

    url = confd.users(payload['uuid'])

    # user update
    new_user_resources = generate_user_resources_bodies(
        context_name=CONTEXT, device=new_device, endpoint_name='def'
    )
    payload.pop('call_record_enabled', None)  # Deprecated field
    response = url.put(
        {**payload, 'lines': [new_user_resources.line]},
        query_string="recursive=True",
    )
    response.assert_updated()

    # retrieve the data for the user and check the lines
    new_line = confd.users(payload['uuid']).get().item['lines'][0]
    assert_that(new_line['id'], is_not(equal_to(first_line_id)))

    # retrieve the line associated to the user and check its data are correct
    assert_that(
        confd.lines(new_line['id']).get().item,
        has_entries(
            extensions=contains(has_entries(**new_user_resources.extension)),
            endpoint_sip=has_entries(
                name=new_user_resources.line['endpoint_sip']['name']
            ),
            device_id=new_device['id'],
        ),
    )

    # update the label of the SIP endpoint
    new_line['endpoint_sip']['label'] = 'new label'
    response = url.put(
        {**payload, 'lines': [new_line]},
        query_string="recursive=True",
    )
    response.assert_updated()

    # retrieve the data for the user and check the lines
    assert_that(
        confd.users(payload['uuid']).get().item,
        has_entries(
            lines=contains(has_entries(endpoint_sip=has_entries(label='new label'))),
        ),
    )

    # user deletion
    response = url.delete(recursive=True)
    response.assert_deleted()

    # verify that user is deleted
    response = url.get()
    response.assert_status(404)

    # verify that line is deleted
    url = confd.lines(new_line['id'])
    response = url.get()
    response.assert_status(404)

    # verify that extension is deleted
    url = confd.extensions(new_line['extensions'][0]['id'])
    response = url.get()
    response.assert_status(404)

    # verify that the device is not deleted
    url = confd.devices(device['id'])
    response = url.get()
    response.assert_ok()


@fixtures.device()
def test_update_lines_sip_sccp_error(
    device,
):
    user_resources = generate_user_resources_bodies(
        context_name=CONTEXT, device=device, endpoint_name='abc'
    )

    user_body = {
        'lines': [user_resources.line],
        **user_resources.user,
    }
    response = confd.users.post(user_body)

    response.assert_created('users')
    payload = response.item

    # retrieve the user and try to update the user with the same data
    user = confd.users(payload['uuid']).get().item
    user.pop('call_record_enabled', None)  # Deprecated field
    user.pop(
        'voicemail', None
    )  # The voicemail cannot be updated directly by calling POST /users
    confd.users(payload['uuid']).put(
        **user,
        query_string="recursive=True",
    ).assert_updated()

    url = confd.users(payload['uuid'])

    # user update
    del payload['lines'][0]['endpoint_sip']
    payload['lines'][0]['endpoint_sccp'] = {}
    payload['lines'][0].pop('caller_id', None)  # cannot set caller id to none
    payload['lines'][0].pop('caller_id_name', None)  # cannot set caller id to none
    payload['lines'][0].pop('caller_id_num', None)  # cannot set caller id to none
    response = url.put(
        {**user, 'lines': [payload['lines'][0]]},
        query_string="recursive=True",
    )
    response.assert_status(400)
    assert_that(
        response.raw,
        equal_to(
            '["There is already an endpoint associated to the line that is not of type SCCP. Cannot update the line with another endpoint type"]\n'
        ),
    )

    # user deletion
    response = url.delete(recursive=True)
    response.assert_deleted()

    # verify that user is deleted
    response = url.get()
    response.assert_status(404)

    # verify that line is deleted
    url = confd.lines(payload['lines'][0]['id'])
    response = url.get()
    response.assert_status(404)

    # verify that extension is deleted
    url = confd.extensions(payload['lines'][0]['extensions'][0]['id'])
    response = url.get()
    response.assert_status(404)

    # verify that the device is not deleted
    url = confd.devices(device['id'])
    response = url.get()
    response.assert_ok()


@fixtures.device()
@fixtures.device()
def test_update_extension_lines_no_error(device, new_device):
    user_resources = generate_user_resources_bodies(
        context_name=CONTEXT, device=device, endpoint_name='abc'
    )

    user_body = {
        'lines': [user_resources.line],
        **user_resources.user,
    }
    response = confd.users.post(user_body)

    response.assert_created('users')
    payload = response.item

    url = confd.users(payload['uuid'])

    # user update
    new_user_resources = generate_user_resources_bodies(
        context_name=CONTEXT, device=new_device, endpoint_name='def'
    )
    created_line = payload['lines'][0]
    created_line['extensions'] = [new_user_resources.extension]

    payload.pop('call_record_enabled', None)  # Deprecated field
    payload['lines'][0].pop('caller_id', None)  # cannot set caller id to none
    payload['lines'][0].pop('caller_id_name', None)  # cannot set caller id to none
    payload['lines'][0].pop('caller_id_num', None)  # cannot set caller id to none
    response = url.put(
        {**payload, 'lines': [created_line]},
        query_string="recursive=True",
    )
    response.assert_updated()

    # retrieve the user
    user = confd.users(payload['uuid']).get().item

    # retrieve the data for the user and check the lines
    assert_that(
        user,
        has_entries(
            lines=contains(
                has_entries(
                    extensions=contains(has_entries(**new_user_resources.extension))
                )
            ),
        ),
    )
    assert_that(
        user,
        has_entries(
            lines=not_(
                contains(
                    has_entries(
                        extensions=contains(has_entries(**user_resources.extension))
                    )
                )
            ),
        ),
    )

    created_line['extensions'][0]['id'] = None
    response = url.put(
        {**payload, 'lines': [created_line]},
        query_string="recursive=True",
    )
    response.assert_status(400)
    assert_that(
        response.raw,
        equal_to(
            '["Input Error - lines: {0: {\'extensions\': {0: {\'id\': [\'Field may not be null.\']}}}}"]\n'
        ),
    )

    # user deletion
    response = url.delete(recursive=True)
    response.assert_deleted()

    # verify that user is deleted
    response = url.get()
    response.assert_status(404)

    # verify that line is deleted
    url = confd.lines(payload['lines'][0]['id'])
    response = url.get()
    response.assert_status(404)

    # verify that the device is not deleted
    url = confd.devices(device['id'])
    response = url.get()
    response.assert_ok()


@fixtures.device()
@fixtures.device()
@fixtures.queue()
@fixtures.queue()
def test_update_agent_no_error(
    device,
    device2,
    queue,
    queue2,
):
    user_resources = generate_user_resources_bodies(
        context_name=CONTEXT,
        device=device,
        queue=queue,
    )

    user_body = {
        'lines': [user_resources.line],
        'agent': user_resources.agent,
        **user_resources.user,
    }
    response = confd.users.post(user_body)

    response.assert_created('users')
    payload = response.item

    agent_id = payload['agent']['id']

    # check the data returned when the user is created
    assert_that(
        payload,
        has_entries(
            uuid=uuid_(),
            agent=has_entries(
                number=user_resources.line['extensions'][0]['exten'],
                firstname=user_resources.user['firstname'],
                queues=contains(
                    has_entries(
                        id=user_resources.agent['queues'][0]['id'],
                        penalty=user_resources.agent['queues'][0]['penalty'],
                        priority=user_resources.agent['queues'][0]['priority'],
                    )
                ),
            ),
            **user_resources.user,
        ),
    )

    # retrieve the agent for the user and check the data
    assert_that(
        confd.agents(agent_id).get().item,
        has_entries(
            number=user_resources.line['extensions'][0]['exten'],
            firstname=user_resources.user['firstname'],
            queues=contains(has_entries(id=queue['id'])),
        ),
    )

    url = confd.users(payload['uuid'])

    # update the agent
    agent_language = 'es_ES'

    payload.pop('call_record_enabled', None)  # Deprecated field
    response = url.put(
        {
            **payload,
            'agent': {'id': agent_id, 'language': agent_language},
        },
        query_string="recursive=True",
    )
    response.assert_updated()

    # retrieve the agent for the user and check the data is up-to-date
    response = url.get()
    payload = response.item

    assert_that(
        confd.agents(agent_id).get().item,
        has_entries(
            language=agent_language,
            firstname=payload['firstname'],
        ),
    )

    # replace the agent

    user_resources2 = generate_user_resources_bodies(
        context_name=CONTEXT,
        device=device2,
        queue=queue2,
    )
    payload.pop('call_record_enabled', None)  # Deprecated field
    response = url.put(
        {
            **payload,
            'agent': user_resources2.agent,
        },
        query_string="recursive=True",
    )
    response.assert_updated()

    # retrieve the agent for the user and check if this is a new agent
    response = url.get()
    payload = response.item
    assert_that(
        payload,
        has_entries(
            agent=has_entries(
                id=is_not(agent_id),
            ),
        ),
    )

    # user deletion
    response = url.delete(recursive=True)
    response.assert_deleted()

    # verify that user is deleted
    response = url.get()
    response.assert_status(404)

    # verify that line is deleted
    url = confd.lines(payload['lines'][0]['id'])
    response = url.get()
    response.assert_status(404)

    # verify that extension is deleted
    url = confd.extensions(payload['lines'][0]['extensions'][0]['id'])
    response = url.get()
    response.assert_status(404)

    # verify that agent is deleted
    url = confd.agents(payload['agent']['id'])
    response = url.get()
    response.assert_status(404)
