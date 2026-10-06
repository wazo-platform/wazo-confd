# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, equal_to, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers.config import INCALL_CONTEXT, MAIN_TENANT, SUB_TENANT
from . import confd


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


@fixtures.extension(exten='_5555556789', context=INCALL_CONTEXT)
@fixtures.extension(exten='_555555XXXX', context=INCALL_CONTEXT)
@fixtures.incall()
@fixtures.incall()
@fixtures.user()
def test_list_with_associated_pattern(
    literal_pattern, wildcard_pattern, incall1, incall2, user
):
    destination = {'type': 'user', 'user_id': user['id']}
    confd.incalls(incall1['id']).put(destination=destination).assert_updated()
    confd.incalls(incall2['id']).put(destination=destination).assert_updated()

    with a.incall_extension(incall1, literal_pattern), a.incall_extension(
        incall2, wildcard_pattern
    ):
        response = confd.users(user['uuid']).callerids.outgoing.get()

    # a leading `_` alone still names one number, but a pattern matching many
    # numbers is not a caller ID anyone could be shown
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
