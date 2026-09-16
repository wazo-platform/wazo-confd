# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, equal_to, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers.config import INCALL_CONTEXT, MAIN_TENANT, SUB_TENANT
from . import confd, create_confd


@fixtures.user()
def test_list_when_no_incall(user):
    response = confd.users(user['uuid']).callerids.outgoing.get()
    expected = [{'type': 'anonymous'}]
    assert_that(response.items, contains_inanyorder(*expected))
    assert_that(response.total, equal_to(1))


@fixtures.extension(exten='5555556789', context=INCALL_CONTEXT)
@fixtures.incall()
@fixtures.user()
def test_list_with_associated_type(extension, incall, user):
    destination = {'type': 'user', 'user_id': user['id']}
    confd.incalls(incall['id']).put(destination=destination).assert_updated()

    with a.incall_extension(incall, extension):
        response = confd.users(user['uuid']).callerids.outgoing.get()

    expected = [
        {'type': 'associated', 'number': '5555556789', 'caller_id_name': ''},
        {'type': 'anonymous'},
    ]
    assert_that(response.items, contains_inanyorder(*expected))
    assert_that(response.total, equal_to(2))


@fixtures.phone_number(main=True, number='5555551234')
@fixtures.extension(exten='5555556789', context=INCALL_CONTEXT)
@fixtures.incall(destination={'type': 'custom', 'command': 'Playback(IGNORED)'})
@fixtures.user()
def test_list_with_main_type(phone_number, extension, incall, user):
    with a.incall_extension(incall, extension):
        response = confd.users(user['uuid']).callerids.outgoing.get()

    # The first created is the main and other are ignored
    expected = [
        {'type': 'main', 'number': '5555551234', 'caller_id_name': ''},
        {'type': 'anonymous'},
    ]
    assert_that(response.items, contains_inanyorder(*expected))
    assert_that(response.total, equal_to(2))


@fixtures.phone_number(shared=True, number='5555551234')
@fixtures.user()
def test_list_with_shared(phone_number, user):
    response = confd.users(user['uuid']).callerids.outgoing.get()

    # The first created is the main and other are ignored
    expected = [
        {'type': 'shared', 'number': '5555551234', 'caller_id_name': ''},
        {'type': 'anonymous'},
    ]
    assert_that(response.items, contains_inanyorder(*expected))
    assert_that(response.total, equal_to(2))


@fixtures.phone_number(main=True, number='5555551234', caller_id_name='Acme Corp')
@fixtures.phone_number(shared=True, number='5555551235')
@fixtures.phone_number(shared=True, number='5555551236', caller_id_name='Support Line')
@fixtures.extension(exten='5555551235', context=INCALL_CONTEXT)
@fixtures.incall()
@fixtures.user()
def test_list_with_all_type(
    main_number, shared_number1, shared_number2, extension, incall, user
):
    destination = {'type': 'user', 'user_id': user['id']}
    confd.incalls(incall['id']).put(destination=destination).assert_updated()

    with a.incall_extension(incall, extension):
        response = confd.users(user['uuid']).callerids.outgoing.get()

    expected = [
        {'type': 'main', 'number': '5555551234', 'caller_id_name': 'Acme Corp'},
        {'type': 'associated', 'number': '5555551235', 'caller_id_name': ''},
        {'type': 'shared', 'number': '5555551236', 'caller_id_name': 'Support Line'},
        {'type': 'anonymous'},
    ]
    assert_that(response.items, contains_inanyorder(*expected))
    assert_that(response.total, equal_to(4))


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.users(main['uuid']).callerids.outgoing.get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(sub['uuid']).callerids.outgoing.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items[0], has_entries(type='anonymous'))


@fixtures.user()
def test_get_default_when_never_set(user):
    response = confd.users(user['uuid']).callerids.outgoing.default.get()

    assert_that(response.item, equal_to({'type': 'default'}))


@fixtures.user()
def test_put_default_token(user):
    url = confd.users(user['uuid']).callerids.outgoing.default
    url.put({'type': 'default'}).assert_updated()

    assert_that(url.get().item, equal_to({'type': 'default'}))


@fixtures.user()
def test_put_anonymous(user):
    url = confd.users(user['uuid']).callerids.outgoing.default
    url.put({'type': 'anonymous'}).assert_updated()

    assert_that(url.get().item, equal_to({'type': 'anonymous'}))


@fixtures.phone_number(main=True, number='+15555551234', caller_id_name='Acme Corp')
@fixtures.user()
def test_put_available_number(phone_number, user):
    url = confd.users(user['uuid']).callerids.outgoing.default
    url.put({'type': 'main', 'number': '+15555551234'}).assert_updated()

    assert_that(
        url.get().item,
        has_entries(type='main', number='+15555551234', caller_id_name='Acme Corp'),
    )


@fixtures.phone_number(shared=True, number='+15555551234')
@fixtures.user()
def test_put_number_matching_semantically(phone_number, user):
    # the same number, sent without the country code
    url = confd.users(user['uuid']).callerids.outgoing.default
    url.put({'type': 'shared', 'number': '5555551234'}).assert_updated()

    assert_that(url.get().item, has_entries(type='shared', number='+15555551234'))


@fixtures.phone_number(shared=True, number='+15555551234')
@fixtures.user()
def test_put_number_not_available_is_rejected(phone_number, user):
    url = confd.users(user['uuid']).callerids.outgoing.default
    response = url.put({'type': 'shared', 'number': '+15550000000'})

    response.assert_status(400)
    # unchanged
    assert_that(url.get().item, equal_to({'type': 'default'}))


@fixtures.user()
def test_put_errors(user):
    url = confd.users(user['uuid']).callerids.outgoing.default

    url.put({}).assert_status(400)
    url.put({'type': 'nonsense'}).assert_status(400)
    # `custom` is reported by the API but must never be accepted
    url.put({'type': 'custom', 'number': '+15555551234'}).assert_status(400)
    # a number is required for the types that carry one
    url.put({'type': 'shared'}).assert_status(400)
    url.put({'type': 'main'}).assert_status(400)
    url.put({'type': 'associated'}).assert_status(400)
    url.put({'type': 'shared', 'number': 'not-a-number'}).assert_status(400)


@fixtures.phone_number(shared=True, number='+15555551234')
@fixtures.user()
def test_get_default_reports_custom_when_no_longer_available(phone_number, user):
    url = confd.users(user['uuid']).callerids.outgoing.default
    url.put({'type': 'shared', 'number': '+15555551234'}).assert_updated()

    confd.phone_numbers(phone_number['uuid']).delete().assert_deleted()

    assert_that(url.get().item, has_entries(type='custom', number='+15555551234'))


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_default_multi_tenant(main, sub):
    response = confd.users(main['uuid']).callerids.outgoing.default.get(
        wazo_tenant=SUB_TENANT
    )
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(main['uuid']).callerids.outgoing.default.put(
        {'type': 'default'}, wazo_tenant=SUB_TENANT
    )
    response.assert_match(404, e.not_found(resource='User'))


@fixtures.phone_number(shared=True, number='+15555551234')
@fixtures.user()
def test_users_me_list(phone_number, user):
    user_confd = create_confd(user_uuid=user['uuid'])

    response = user_confd.users.me.callerids.outgoing.get()

    expected = [
        {'type': 'shared', 'number': '+15555551234', 'caller_id_name': ''},
        {'type': 'anonymous'},
    ]
    assert_that(response.items, contains_inanyorder(*expected))


@fixtures.phone_number(shared=True, number='+15555551234')
@fixtures.user()
def test_users_me_default_round_trip(phone_number, user):
    user_confd = create_confd(user_uuid=user['uuid'])
    url = user_confd.users.me.callerids.outgoing.default

    assert_that(url.get().item, equal_to({'type': 'default'}))

    url.put({'type': 'shared', 'number': '+15555551234'}).assert_updated()

    assert_that(url.get().item, has_entries(type='shared', number='+15555551234'))
    # and the admin API sees the same value
    assert_that(
        confd.users(user['uuid']).callerids.outgoing.default.get().item,
        has_entries(type='shared', number='+15555551234'),
    )


@fixtures.phone_number(shared=True, number='+15555551234')
@fixtures.user()
@fixtures.user()
def test_users_me_default_is_per_user(phone_number, user1, user2):
    user1_confd = create_confd(user_uuid=user1['uuid'])
    user2_confd = create_confd(user_uuid=user2['uuid'])

    user1_confd.users.me.callerids.outgoing.default.put(
        {'type': 'shared', 'number': '+15555551234'}
    ).assert_updated()

    assert_that(
        user2_confd.users.me.callerids.outgoing.default.get().item,
        equal_to({'type': 'default'}),
    )


@fixtures.phone_number(shared=True, number='+15555551234', caller_id_name='N' * 256)
@fixtures.user()
def test_put_number_whose_caller_id_name_would_overflow(phone_number, user):
    # the column holding the composed value is shorter than a caller_id_name is
    # allowed to be, so the name is dropped rather than the write failing
    url = confd.users(user['uuid']).callerids.outgoing.default
    url.put({'type': 'shared', 'number': '+15555551234'}).assert_updated()

    assert_that(url.get().item, has_entries(type='shared', number='+15555551234'))


@fixtures.phone_number(shared=True, number='+' + '1' * 100)
@fixtures.user()
def test_put_number_too_long_for_the_column_is_rejected(phone_number, user):
    url = confd.users(user['uuid']).callerids.outgoing.default
    response = url.put({'type': 'shared', 'number': '+' + '1' * 100})

    response.assert_status(400)
    assert_that(url.get().item, equal_to({'type': 'default'}))


@fixtures.phone_number(shared=True, number='+14445551234', caller_id_name='Acme')
@fixtures.user()
def test_get_default_set_through_the_user_api_with_an_unquoted_name(phone_number, user):
    # the user API and the dialplan both accept an unquoted name, and the number
    # must still be reported as a number rather than as the whole stored string
    confd.users(user['uuid']).put(
        outgoing_caller_id='Hursule <4445551234>'
    ).assert_updated()

    item = confd.users(user['uuid']).callerids.outgoing.default.get().item

    assert_that(item, has_entries(type='shared', number='4445551234'))
