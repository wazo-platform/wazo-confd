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
from xivo_test_helpers.confd.config import INCALL_CONTEXT, CONTEXT
from . import confd


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
@fixtures.extension()
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
def test_dissociate(incall, extension):
    with a.incall_extension(incall, extension, check=False):
        response = confd.incalls(incall['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_get_incall_relation(incall, extension):
    expected = has_entries(
        extensions=contains(has_entries(id=extension['id'],
                                        exten=extension['exten'],
                                        context=extension['context']))
    )

    with a.incall_extension(incall, extension):
        response = confd.incalls(incall['id']).get()
        assert_that(response.item, expected)


@fixtures.extension(context=INCALL_CONTEXT)
@fixtures.incall()
def test_get_extension_relation(extension, incall):
    expected = has_entries(
        incall=has_entries(id=incall['id'])
    )

    with a.incall_extension(incall, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(response.item, expected)


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_edit_context_to_internal_when_associated(incall, extension):
    with a.incall_extension(incall, extension):
        response = confd.extensions(extension['id']).put(context=CONTEXT)
        response.assert_status(400)


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_delete_incall_when_incall_and_extension_associated(incall, extension):
    with a.incall_extension(incall, extension, check=False):
        response = confd.incalls(incall['id']).delete()
        response.assert_deleted()


def test_delete_extension_when_incall_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
