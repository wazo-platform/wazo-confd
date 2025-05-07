# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
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
        {'type': 'associated', 'number': '5555556789'},
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
        {'type': 'main', 'number': '5555551234'},
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
        {'type': 'shared', 'number': '5555551234'},
        {'type': 'anonymous'},
    ]
    assert_that(response.items, contains_inanyorder(*expected))
    assert_that(response.total, equal_to(2))


@fixtures.phone_number(main=True, number='5555551234')
@fixtures.phone_number(shared=True, number='5555551235')
@fixtures.phone_number(shared=True, number='5555551236')
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
        {'type': 'main', 'number': '5555551234'},
        {'type': 'associated', 'number': '5555551235'},
        {'type': 'shared', 'number': '5555551236'},
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
