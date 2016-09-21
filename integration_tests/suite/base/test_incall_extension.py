# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from hamcrest import (assert_that,
                      contains_inanyorder,
                      empty,
                      has_entries)

from test_api import scenarios as s
from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import associations as a
from test_api.config import INCALL_CONTEXT


FAKE_ID = 999999999


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_errors(incall, extension):
    fake_incall = confd.incalls(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.incalls(incall['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_incall, 'Incall'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_dissociate_errors(incall, extension):
    fake_incall_extension = confd.incalls(incall['id']).extensions(extension['id']).delete
    fake_incall = confd.incalls(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.incalls(incall['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_incall, 'Incall'
    yield s.check_resource_not_found, fake_extension, 'Extension'
    yield s.check_resource_not_found, fake_incall_extension, 'IncallExtension'


def test_get_errors():
    fake_incall = confd.incalls(FAKE_ID).extensions.get
    fake_extension = confd.extensions(FAKE_ID).incalls.get

    yield s.check_resource_not_found, fake_incall, 'Incall'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate(incall, extension):
    response = confd.incalls(incall['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_already_associated(incall, extension):
    with a.incall_extension(incall, extension):
        response = confd.incalls(incall['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('Incall', 'Extension'))


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_multiple_extensions_to_incall(incall, extension1, extension2):
    with a.incall_extension(incall, extension1):
        response = confd.incalls(incall['id']).extensions(extension2['id']).put()
        response.assert_match(400, e.resource_associated('Incall', 'Extension'))


@fixtures.incall()
@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_multiple_incalls_to_extension(incall1, incall2, extension):
    with a.incall_extension(incall1, extension):
        response = confd.incalls(incall2['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('Incall', 'Extension'))


@fixtures.incall()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()  # Cannot have context=INCALL_CONTEXT, since line_extension can associate incall ..
def test_associate_when_user_already_associated(incall, user, line_sip, extension):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = confd.incalls(incall['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('user', 'Extension'))


@fixtures.incall()
@fixtures.extension()
def test_associate_when_not_incall_context(incall, extension):
    response = confd.incalls(incall['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_get_extensions_associated_to_incall(incall, extension):
    expected = contains_inanyorder(has_entries({'incall_id': incall['id'],
                                                'extension_id': extension['id']}))

    with a.incall_extension(incall, extension):
        response = confd.incalls(incall['id']).extensions.get()
        assert_that(response.items, expected)


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_get_incalls_associated_to_extension(incall, extension):
    expected = contains_inanyorder(has_entries({'incall_id': incall['id'],
                                                'extension_id': extension['id']}))

    with a.incall_extension(incall, extension):
        response = confd.extensions(extension['id']).incalls.get()
        assert_that(response.items, expected)


@fixtures.incall()
def test_get_no_extension(incall):
    response = confd.incalls(incall['id']).extensions.get()
    assert_that(response.items, empty())


@fixtures.extension()
def test_get_no_incall(extension):
    response = confd.extensions(extension['id']).incalls.get()
    assert_that(response.items, empty())


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_dissociate(incall, extension):
    with a.incall_extension(incall, extension, check=False):
        response = confd.incalls(incall['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_delete_incall_when_incall_and_extension_associated(incall, extension):
    with a.incall_extension(incall, extension, check=False):
        confd.incalls(incall['id']).delete().assert_deleted()

        deleted_incall = confd.incalls(incall['id']).extensions.get
        yield s.check_resource_not_found, deleted_incall, 'Incall'

        response = confd.extensions(extension['id']).incalls.get()
        yield assert_that, response.items, empty()


def test_delete_extension_when_incall_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
