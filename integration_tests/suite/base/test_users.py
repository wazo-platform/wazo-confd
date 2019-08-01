# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains,
    empty,
    equal_to,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    none,
    not_,
)

from . import confd
from ..helpers import (
    associations as a,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

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
    "call_record_enabled": True,
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
    "call_record_enabled": False,
    "online_call_record_enabled": False,
    "call_permission_password": None,
    "enabled": True,
    "ring_seconds": 30,
    "simultaneous_calls": 5,
}


def test_search_errors():
    url = confd.users.get
    s.search_error_checks(url)


def test_head_errors():
    response = confd.users(999999).head()
    response.assert_status(404)


def test_get_errors():
    fake_get = confd.users(999999).get
    s.check_resource_not_found(fake_get, 'User')


def test_post_errors():
    empty_post = confd.users.post
    user_post = confd.users(firstname="Jôhn").post

    s.check_missing_required_field_returns_error(empty_post, 'firstname')
    error_checks(user_post)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'firstname', 123)
    s.check_bogus_field_returns_error(url, 'firstname', None)
    s.check_bogus_field_returns_error(url, 'firstname', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'firstname', {})
    s.check_bogus_field_returns_error(url, 'firstname', [])
    s.check_bogus_field_returns_error(url, 'lastname', 123)
    s.check_bogus_field_returns_error(url, 'lastname', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'lastname', {})
    s.check_bogus_field_returns_error(url, 'lastname', [])
    s.check_bogus_field_returns_error(url, 'email', s.random_string(255))
    s.check_bogus_field_returns_error(url, 'email', 123)
    s.check_bogus_field_returns_error(url, 'email', 'invalid_email')
    s.check_bogus_field_returns_error(url, 'email', {})
    s.check_bogus_field_returns_error(url, 'email', [])
    s.check_bogus_field_returns_error(url, 'timezone', 123)
    s.check_bogus_field_returns_error(url, 'timezone', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'timezone', {})
    s.check_bogus_field_returns_error(url, 'timezone', [])
    s.check_bogus_field_returns_error(url, 'language', 123)
    s.check_bogus_field_returns_error(url, 'language', 'klingon')
    s.check_bogus_field_returns_error(url, 'language', {})
    s.check_bogus_field_returns_error(url, 'language', [])
    s.check_bogus_field_returns_error(url, 'description', 123)
    s.check_bogus_field_returns_error(url, 'description', {})
    s.check_bogus_field_returns_error(url, 'description', [])
    s.check_bogus_field_returns_error(url, 'caller_id', 123)
    s.check_bogus_field_returns_error(url, 'caller_id', 'invalid_regex')
    s.check_bogus_field_returns_error(url, 'caller_id', s.random_string(161))
    s.check_bogus_field_returns_error(url, 'caller_id', {})
    s.check_bogus_field_returns_error(url, 'caller_id', [])
    s.check_bogus_field_returns_error(url, 'outgoing_caller_id', 123)
    s.check_bogus_field_returns_error(url, 'outgoing_caller_id', s.random_string(81))
    s.check_bogus_field_returns_error(url, 'outgoing_caller_id', {})
    s.check_bogus_field_returns_error(url, 'outgoing_caller_id', [])
    s.check_bogus_field_returns_error(url, 'mobile_phone_number', 123)
    s.check_bogus_field_returns_error(url, 'mobile_phone_number', 'invalid_regex')
    s.check_bogus_field_returns_error(url, 'mobile_phone_number', '123abcd')
    s.check_bogus_field_returns_error(url, 'mobile_phone_number', s.random_string(81))
    s.check_bogus_field_returns_error(url, 'mobile_phone_number', {})
    s.check_bogus_field_returns_error(url, 'mobile_phone_number', [])
    s.check_bogus_field_returns_error(url, 'username', 123)
    s.check_bogus_field_returns_error(url, 'username', 'invalid_régex')
    s.check_bogus_field_returns_error(url, 'username', s.random_string(1))
    s.check_bogus_field_returns_error(url, 'username', s.random_string(255))
    s.check_bogus_field_returns_error(url, 'username', {})
    s.check_bogus_field_returns_error(url, 'username', [])
    s.check_bogus_field_returns_error(url, 'password', 123)
    s.check_bogus_field_returns_error(url, 'password', 'invalid_régex')
    s.check_bogus_field_returns_error(url, 'password', s.random_string(3))
    s.check_bogus_field_returns_error(url, 'password', s.random_string(65))
    s.check_bogus_field_returns_error(url, 'password', {})
    s.check_bogus_field_returns_error(url, 'password', [])
    s.check_bogus_field_returns_error(url, 'music_on_hold', 123)
    s.check_bogus_field_returns_error(url, 'music_on_hold', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'music_on_hold', {})
    s.check_bogus_field_returns_error(url, 'music_on_hold', [])
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', 123)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', s.random_string(40))
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', {})
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', [])
    s.check_bogus_field_returns_error(url, 'userfield', 123)
    s.check_bogus_field_returns_error(url, 'userfield', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'userfield', {})
    s.check_bogus_field_returns_error(url, 'userfield', [])
    s.check_bogus_field_returns_error(url, 'caller_id', 'invalid')
    s.check_bogus_field_returns_error(url, 'caller_id', 1234)
    s.check_bogus_field_returns_error(url, 'caller_id', s.random_string(161))
    s.check_bogus_field_returns_error(url, 'caller_id', {})
    s.check_bogus_field_returns_error(url, 'caller_id', [])
    s.check_bogus_field_returns_error(url, 'call_transfer_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'call_transfer_enabled', 123)
    s.check_bogus_field_returns_error(url, 'call_transfer_enabled', {})
    s.check_bogus_field_returns_error(url, 'call_transfer_enabled', [])
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_enabled', 123)
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_enabled', {})
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_enabled', [])
    s.check_bogus_field_returns_error(url, 'call_record_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'call_record_enabled', 123)
    s.check_bogus_field_returns_error(url, 'call_record_enabled', {})
    s.check_bogus_field_returns_error(url, 'call_record_enabled', [])
    s.check_bogus_field_returns_error(url, 'online_call_record_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'online_call_record_enabled', 123)
    s.check_bogus_field_returns_error(url, 'online_call_record_enabled', {})
    s.check_bogus_field_returns_error(url, 'online_call_record_enabled', [])
    s.check_bogus_field_returns_error(url, 'supervision_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'supervision_enabled', 123)
    s.check_bogus_field_returns_error(url, 'supervision_enabled', {})
    s.check_bogus_field_returns_error(url, 'supervision_enabled', [])
    s.check_bogus_field_returns_error(url, 'simultaneous_calls', 'sixty')
    s.check_bogus_field_returns_error(url, 'simultaneous_calls', -1)
    s.check_bogus_field_returns_error(url, 'simultaneous_calls', 21)
    s.check_bogus_field_returns_error(url, 'simultaneous_calls', {})
    s.check_bogus_field_returns_error(url, 'simultaneous_calls', [])
    s.check_bogus_field_returns_error(url, 'ring_seconds', 'ten')
    s.check_bogus_field_returns_error(url, 'ring_seconds', -1)
    s.check_bogus_field_returns_error(url, 'ring_seconds', 61)
    s.check_bogus_field_returns_error(url, 'ring_seconds', {})
    s.check_bogus_field_returns_error(url, 'ring_seconds', [])
    s.check_bogus_field_returns_error(url, 'call_permission_password', 1234)
    s.check_bogus_field_returns_error(url, 'call_permission_password', 'invalid_char')
    s.check_bogus_field_returns_error(url, 'call_permission_password', {})
    s.check_bogus_field_returns_error(url, 'call_permission_password', [])
    s.check_bogus_field_returns_error(url, 'call_permission_password', s.random_string(17))
    s.check_bogus_field_returns_error(url, 'subscription_type', 'one')
    s.check_bogus_field_returns_error(url, 'subscription_type', -1)
    s.check_bogus_field_returns_error(url, 'subscription_type', 11)
    s.check_bogus_field_returns_error(url, 'subscription_type', {})
    s.check_bogus_field_returns_error(url, 'subscription_type', [])
    s.check_bogus_field_returns_error(url, 'enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'enabled', 123)
    s.check_bogus_field_returns_error(url, 'enabled', {})
    s.check_bogus_field_returns_error(url, 'enabled', [])


def put_error_checks(url):
    s.check_bogus_field_returns_error(url, 'caller_id', None)
    s.check_bogus_field_returns_error(url, 'call_transfer_enabled', None)
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_enabled', None)
    s.check_bogus_field_returns_error(url, 'call_record_enabled', None)
    s.check_bogus_field_returns_error(url, 'online_call_record_enabled', None)
    s.check_bogus_field_returns_error(url, 'supervision_enabled', None)
    s.check_bogus_field_returns_error(url, 'ring_seconds', None)
    s.check_bogus_field_returns_error(url, 'simultaneous_calls', None)
    s.check_bogus_field_returns_error(url, 'ring_seconds', None)
    s.check_bogus_field_returns_error(url, 'enabled', None)


def test_put_errors():
    with fixtures.user() as user:
        user_put = confd.users(user['id']).put

        error_checks(user_put)
        put_error_checks(user_put)



def test_unique_errors():
    with fixtures.user(firstname='user1', username='unique_username', email='unique@email.com') as user1, fixtures.user() as user2:
        url = confd.users(user2['id']).put
        unique_error_checks(url, user1)

        required_body = {'firstname': 'user2'}
        url = confd.users.post
        unique_error_checks(url, user1, required_body)



def unique_error_checks(url, existing_resource, required_body=None):
    s.check_bogus_field_returns_error(url, 'username', existing_resource['username'], required_body)
    s.check_bogus_field_returns_error(url, 'email', existing_resource['email'], required_body)


def test_delete_errors():
    with fixtures.user() as user:
        user_url = confd.users(user['id'])
        user_url.delete()
        s.check_resource_not_found(user_url.get, 'User')



def test_that_the_directory_view_works_with_unicode_characters():
    with fixtures.user(firstname='ÉricDir') as user:
        response = confd.users.get(view='directory', search='éricdir')
        response.assert_ok()

        assert_that(response.items[0]['id'], equal_to(user['id']))



def test_summary_view_on_sip_endpoint():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension:
        with a.line_endpoint_sip(line, sip), a.line_extension(line, extension), \
            a.user_line(user, line):

            response = confd.users.get(view='summary', id=user['id'])
            assert_that(
                response.items,
                contains(has_entries(
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
                ))
            )


def test_summary_view_on_sccp_endpoint():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sccp() as sccp, fixtures.extension() as extension:
        with a.line_endpoint_sccp(line, sccp), a.line_extension(line, extension), \
            a.user_line(user, line):

            response = confd.users.get(view='summary', id=user['id'])
            assert_that(
                response.items,
                contains(has_entries(
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
                ))
            )


def test_summary_view_on_custom_endpoint():
    with fixtures.user() as user, fixtures.line() as line, fixtures.custom() as custom, fixtures.extension() as extension:
        with a.line_endpoint_custom(line, custom), a.line_extension(line, extension), \
            a.user_line(user, line):

            response = confd.users.get(view='summary', id=user['id'])
            assert_that(
                response.items,
                contains(has_entries(
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
                ))
            )


def test_summary_view_on_user_without_line():
    with fixtures.user() as user:
        response = confd.users.get(view='summary', id=user['id'])
        assert_that(
            response.items,
            contains(has_entries(
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
            ))
        )



def test_search_using_legacy_parameter():
    with fixtures.user(firstname="Lègacy", lastname="Usér") as user1, fixtures.user(firstname="Hîde", lastname="Mé") as user2:
        response = confd.users.get(q="lègacy usér")
        assert_that(response.items, has_item(has_entries(firstname="Lègacy", lastname="Usér")))
        assert_that(response.items, is_not(has_item(has_entries(firstname="Hîde", lastname="Mé"))))



def test_search_on_user_view():
    with fixtures.user(
    firstname="Léeroy",
    lastname="Jénkins",
    email="jenkins@leeroy.com",
    outgoing_caller_id='"Mystery Man" <5551234567>',
    username="leeroyjenkins",
    music_on_hold="leeroy_music_on_hold",
    mobile_phone_number="5552423232",
    userfield="leeroy jenkins userfield",
    description="Léeroy Jénkin's bio",
    enabled=False,
    preprocess_subroutine="leeroy_preprocess",
) as user:
        url = confd.users
        searches = {
            'firstname': 'léeroy',
            'lastname': 'jénkins',
            'email': 'jenkins@',
            'music_on_hold': 'leeroy_music',
            'outgoing_caller_id': '5551234567',
            'mobile_phone_number': '2423232',
            'userfield': 'jenkins userfield',
            'description': "jénkin's bio",
            'preprocess_subroutine': 'roy_preprocess',
        }

        for field, term in searches.items():
            check_search(url, field, term, user[field])



def test_search_on_directory_view():
    with fixtures.user(
    firstname="Môustapha",
    lastname="Bângoura",
    email="moustapha@bangoura.com",
    mobile_phone_number="+5559284759",
    userfield="Moustapha userfield",
    description="Moustapha the greatest dancer",
) as user:
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
            check_search(url, field, term, user[field])



def test_search_on_users_extension():
    with fixtures.user() as user, fixtures.line_sip() as line, fixtures.extension() as extension:
        with a.user_line(user, line), a.line_extension(line, extension):
            response = confd.users.get(search=extension['exten'], view='directory')
            assert_that(response.items, has_item(has_entry('exten', extension['exten'])))


def test_search_on_users_with_context_filter():
    with fixtures.user(firstname='context-filter') as user, fixtures.line_sip() as line, fixtures.extension() as extension:
        with a.user_line(user, line), a.line_extension(line, extension):
            response = confd.users.get(firstname='context-filter', view='directory', context='default')
            assert_that(response.total, equal_to(1))
            assert_that(response.items, has_item(has_entry('exten', extension['exten'])))

            response = confd.users.get(firstname='context-filter', view='directory', context='other')
            assert_that(response.total, equal_to(0))


def test_search_on_summary_view():
    with fixtures.user(
    firstname="Âboubacar",
    lastname="Manè",
    description="Âboubacar le grand danseur",
) as user, fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension:
        url = confd.users(view='summary')

        with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(line, extension):
            check_search(url, 'firstname', 'âbou', user['firstname'])
            check_search(url, 'lastname', 'man', user['lastname'])
            check_search(url, 'provisioning_code', line['provisioning_code'], line['provisioning_code'])
            check_search(url, 'extension', extension['exten'], extension['exten'])



def check_search(url, field, term, value):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, value)))


def test_list_multi_tenant():
    with fixtures.user(wazo_tenant=MAIN_TENANT) as main, fixtures.user(wazo_tenant=SUB_TENANT) as sub:
        response = confd.users.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(has_item(main)), not_(has_item(sub)),
        )

        response = confd.users.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_item(sub), not_(has_item(main))),
        )

        response = confd.users.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(main, sub),
        )



def test_sorting_offset_limit():
    with fixtures.user(
    firstname="firstname1",
    lastname="lastname1",
    email="email1@example.com",
    mobile_phone_number="+5551",
    userfield="sort userfield1",
    description="description1",
) as user1, fixtures.user(
    firstname="firstname2",
    lastname="lastname2",
    email="email2@example.com",
    mobile_phone_number="+5552",
    userfield="sort userfield2",
    description="description2",
) as user2:
        url = confd.users.get
        s.check_sorting(url, user1, user2, 'firstname', 'firstname')
        s.check_sorting(url, user1, user2, 'lastname', 'lastname')
        s.check_sorting(url, user1, user2, 'email', 'email')
        s.check_sorting(url, user1, user2, 'mobile_phone_number', '+555')
        s.check_sorting(url, user1, user2, 'userfield', 'sort userfield')
        s.check_sorting(url, user1, user2, 'description', 'description')

        s.check_offset(url, user1, user2, 'firstname', 'firstname')
        s.check_offset_legacy(url, user1, user2, 'firstname', 'firstname')

        s.check_limit(url, user1, user2, 'firstname', 'firstname')



def test_head_user():
    with fixtures.user() as user:
        response = confd.users(user['uuid']).head()
        response.assert_ok()



def test_get_user():
    with fixtures.user(**FULL_USER) as user:
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
                services={
                    'dnd': {'enabled': False},
                    'incallfilter': {'enabled': False},
                },
                voicemail=none(),
                queues=empty(),
            )
        )



def test_that_get_works_with_a_uuid():
    with fixtures.user(firstname="Snôm", lastname="Whîte") as user_1, fixtures.user() as user_2_, fixtures.user() as user_3:
        result = confd.users(user_1['uuid']).get()

        assert_that(result.item, has_entries(firstname='Snôm', lastname='Whîte'))



def test_that_the_username_can_be_an_email():
    with fixtures.user(firstname="Snôw", lastname="Whîte", username='snow.white+dwarves@disney.example.com') as user:
        result = confd.users(user['id']).get()

        assert_that(result.item, has_entries(
            firstname='Snôw',
            lastname='Whîte',
            username='snow.white+dwarves@disney.example.com',
        ))



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
            call_record_enabled=False,
            online_call_record_enabled=False,
            supervision_enabled=True,
            ring_seconds=30,
            simultaneous_calls=5,
        )
    )


def test_create_user_with_all_parameters():
    response = confd.users.post(**FULL_USER)

    response.assert_created('users')
    assert_that(response.item, has_entries(FULL_USER))
    assert_that(response.item, has_entries(created_at=is_not(none())))


def test_create_user_with_all_parameters_null():
    response = confd.users.post(**NULL_USER)
    assert_that(response.item, has_entries(NULL_USER))


def test_create_user_generates_appropriate_caller_id():
    response = confd.users.post(firstname='Jôhn')
    assert_that(response.item, has_entry('caller_id', '"Jôhn"'))

    response = confd.users.post(firstname='Jôhn', lastname='Doe')
    assert_that(response.item['caller_id'], equal_to('"Jôhn Doe"'))


def test_update_user_with_all_parameters():
    with fixtures.user(
    firstname="Léeroy",
    lastname="Jénkins",
    email="leeroy@jenkins.com",
    outgoing_caller_id='"Mystery Man" <5551234567>',
    username="leeroyjenkins",
    music_on_hold="leeroy_music_on_hold",
    mobile_phone_number="5552423232",
    userfield="leeroy jenkins userfield",
    description="Léeroy Jénkin's bio",
    preprocess_subroutine="leeroy_preprocess",
) as user:
        user_url = confd.users(user['id'])

        response = user_url.put(**FULL_USER)
        response.assert_updated()

        response = user_url.get()
        assert_that(response.item, has_entries(FULL_USER))



def test_update_user_with_all_parameters_null():
    with fixtures.user() as user:
        response = confd.users(user['id']).put(**NULL_USER)
        response.assert_updated()

        response = confd.users(user['id']).get()
        assert_that(response.item, has_entries(**NULL_USER))



def test_that_users_can_be_edited_by_uuid():
    with fixtures.user() as user:
        response = confd.users(user['uuid']).put({'firstname': 'Fôo', 'lastname': 'Bâr'})
        response.assert_updated()

        response = confd.users(user['uuid']).get()
        assert_that(response.item, has_entries(firstname='Fôo', lastname='Bâr'))



def test_delete():
    with fixtures.user() as user:
        response = confd.users(user['id']).delete()
        response.assert_deleted()



def test_that_users_can_be_deleted_by_uuid():
    with fixtures.user() as user:
        response = confd.users(user['uuid']).delete()
        response.assert_deleted()

        response = confd.users(user['uuid']).get()
        response.assert_status(404)



def test_bus_events():
    with fixtures.user() as user:
        required_body = {'firstname': 'test-event-user'}
        s.check_bus_event('config.user.created', confd.users.post, required_body)
        s.check_bus_event('config.user.edited', confd.users(user['id']).put)
        s.check_bus_event('config.user.deleted', confd.users(user['id']).delete)

