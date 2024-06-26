# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
)
from ..helpers.config import INCALL_CONTEXT, MAIN_TENANT, SUB_TENANT


@fixtures.user()
def test_list_when_no_incall(user):
    response = confd.users(user['uuid']).callerids.outgoing.get()
    expected = [{'type': 'anonymous'}]
    assert_that(response.items, contains_inanyorder(*expected))
    assert_that(response.total, equal_to(1))


@fixtures.extension(exten='5555551234', context=INCALL_CONTEXT)
@fixtures.incall()
@fixtures.extension(exten='5555556789', context=INCALL_CONTEXT)
@fixtures.incall()
@fixtures.user()
def test_list_with_associated_type(extension1, incall1, extension2, incall2, user):
    destination = {'type': 'user', 'user_id': user['id']}
    confd.incalls(incall1['id']).put(destination=destination).assert_updated()
    confd.incalls(incall2['id']).put(destination=destination).assert_updated()

    with a.incall_extension(incall1, extension1):
        with a.incall_extension(incall2, extension2):
            response = confd.users(user['uuid']).callerids.outgoing.get()

    expected = [
        {'type': 'main', 'number': '5555551234'},
        {'type': 'associated', 'number': '5555551234'},
        {'type': 'associated', 'number': '5555556789'},
        {'type': 'anonymous'},
    ]
    assert_that(response.items, contains_inanyorder(*expected))
    assert_that(response.total, equal_to(4))


@fixtures.extension(exten='5555551234', context=INCALL_CONTEXT)
@fixtures.incall(destination={'type': 'custom', 'command': 'Playback(Welcome)'})
@fixtures.extension(exten='5555556789', context=INCALL_CONTEXT)
@fixtures.incall(destination={'type': 'custom', 'command': 'Playback(IGNORED)'})
@fixtures.user()
def test_list_with_main_type(extension1, incall1, extension2, incall2, user):
    with a.incall_extension(incall1, extension1):
        with a.incall_extension(incall2, extension2):
            response = confd.users(user['uuid']).callerids.outgoing.get()

    # The first created is the main and other are ignored
    expected = [
        {'type': 'main', 'number': '5555551234'},
        {'type': 'anonymous'},
    ]
    assert_that(response.items, contains_inanyorder(*expected))
    assert_that(response.total, equal_to(2))


@fixtures.extension(exten='5555551234', context=INCALL_CONTEXT)
@fixtures.incall(destination={'type': 'custom', 'command': 'Playback(Welcome)'})
@fixtures.extension(exten='5555556789', context=INCALL_CONTEXT)
@fixtures.incall()
@fixtures.user()
def test_list_with_all_type(main_extension, main_incall, extension, incall, user):
    destination = {'type': 'user', 'user_id': user['id']}
    confd.incalls(incall['id']).put(destination=destination).assert_updated()

    with a.incall_extension(main_incall, main_extension):
        with a.incall_extension(incall, extension):
            response = confd.users(user['uuid']).callerids.outgoing.get()

    expected = [
        {'type': 'main', 'number': '5555551234'},
        {'type': 'associated', 'number': '5555556789'},
        {'type': 'anonymous'},
    ]
    assert_that(response.items, contains_inanyorder(*expected))
    assert_that(response.total, equal_to(3))


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.users(main['uuid']).callerids.outgoing.get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(sub['uuid']).callerids.outgoing.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items[0], has_entries(type='anonymous'))
