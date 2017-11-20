# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      contains,
                      has_entries)
from ..helpers import scenarios as s
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import associations as a
from xivo_test_helpers.confd.config import INCALL_CONTEXT
from . import confd


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
