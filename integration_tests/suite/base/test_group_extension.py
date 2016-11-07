# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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
                      contains,
                      has_entries)
from test_api import scenarios as s
from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import associations as a
from test_api.config import INCALL_CONTEXT


FAKE_ID = 999999999


@fixtures.group()
@fixtures.extension()
def test_associate_errors(group, extension):
    fake_group = confd.groups(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.groups(group['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_group, 'Group'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.group()
@fixtures.extension()
def test_dissociate_errors(group, extension):
    fake_group_extension = confd.groups(group['id']).extensions(extension['id']).delete
    fake_group = confd.groups(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.groups(group['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_group, 'Group'
    yield s.check_resource_not_found, fake_extension, 'Extension'
    yield s.check_resource_not_found, fake_group_extension, 'GroupExtension'


@fixtures.group()
@fixtures.extension()
def test_associate(group, extension):
    response = confd.groups(group['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.group()
@fixtures.extension()
def test_associate_already_associated(group, extension):
    with a.group_extension(group, extension):
        response = confd.groups(group['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('Group', 'Extension'))


@fixtures.group()
@fixtures.extension()
@fixtures.extension()
def test_associate_multiple_extensions_to_group(group, extension1, extension2):
    with a.group_extension(group, extension1):
        response = confd.groups(group['id']).extensions(extension2['id']).put()
        response.assert_match(400, e.resource_associated('Group', 'Extension'))


@fixtures.group()
@fixtures.group()
@fixtures.extension()
def test_associate_multiple_groups_to_extension(group1, group2, extension):
    with a.group_extension(group1, extension):
        response = confd.groups(group2['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('Group', 'Extension'))


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_when_user_already_associated(group, user, line_sip, extension):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = confd.groups(group['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('user', 'Extension'))


@fixtures.group()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_when_not_internal_context(group, extension):
    response = confd.groups(group['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.group()
@fixtures.extension()
def test_dissociate(group, extension):
    with a.group_extension(group, extension, check=False):
        response = confd.groups(group['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.group()
@fixtures.extension()
def test_get_group_relation(group, extension):
    with a.group_extension(group, extension):
        response = confd.groups(group['id']).get()
        assert_that(response.item, has_entries(
            extensions=contains(has_entries(id=extension['id'],
                                            exten=extension['exten'],
                                            context=extension['context']))
        ))


@fixtures.extension()
@fixtures.group()
def test_get_extension_relation(extension, group):
    with a.group_extension(group, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(response.item, has_entries(
            group=has_entries(id=group['id'],
                              name=group['name'])
        ))


@fixtures.group()
@fixtures.extension()
def test_edit_context_to_incall_when_associated(group, extension):
    with a.group_extension(group, extension):
        response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
        response.assert_status(400)


@fixtures.group()
@fixtures.extension()
def test_delete_group_when_group_and_extension_associated(group, extension):
    with a.group_extension(group, extension, check=False):
        response = confd.groups(group['id']).delete()
        response.assert_deleted()


def test_delete_extension_when_group_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
