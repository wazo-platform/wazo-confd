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
from ..helpers.config import INCALL_CONTEXT
from . import confd


FAKE_ID = 999999999


@fixtures.conference()
@fixtures.extension()
def test_associate_errors(conference, extension):
    fake_conference = confd.conferences(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.conferences(conference['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_conference, 'Conference'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.conference()
@fixtures.extension()
def test_dissociate_errors(conference, extension):
    fake_conference = confd.conferences(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.conferences(conference['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_conference, 'Conference'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.conference()
@fixtures.extension()
def test_associate(conference, extension):
    response = confd.conferences(conference['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.conference()
@fixtures.extension()
def test_associate_already_associated(conference, extension):
    with a.conference_extension(conference, extension):
        response = confd.conferences(conference['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.conference()
@fixtures.extension()
@fixtures.extension()
def test_associate_multiple_extensions_to_conference(conference, extension1, extension2):
    with a.conference_extension(conference, extension1):
        response = confd.conferences(conference['id']).extensions(extension2['id']).put()
        response.assert_match(400, e.resource_associated('Conference', 'Extension'))


@fixtures.conference()
@fixtures.conference()
@fixtures.extension()
def test_associate_multiple_conferences_to_extension(conference1, conference2, extension):
    with a.conference_extension(conference1, extension):
        response = confd.conferences(conference2['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('Conference', 'Extension'))


@fixtures.conference()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_when_user_already_associated(conference, user, line_sip, extension):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = confd.conferences(conference['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('user', 'Extension'))


@fixtures.conference()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_when_not_internal_context(conference, extension):
    response = confd.conferences(conference['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.conference()
@fixtures.extension()
def test_dissociate(conference, extension):
    with a.conference_extension(conference, extension, check=False):
        response = confd.conferences(conference['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.conference()
@fixtures.extension()
def test_dissociate_not_associated(conference, extension):
    response = confd.conferences(conference['id']).extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.conference()
@fixtures.extension()
def test_get_conference_relation(conference, extension):
    with a.conference_extension(conference, extension):
        response = confd.conferences(conference['id']).get()
        assert_that(response.item, has_entries(
            extensions=contains(has_entries(id=extension['id'],
                                            exten=extension['exten'],
                                            context=extension['context']))
        ))


@fixtures.extension()
@fixtures.conference()
def test_get_extension_relation(extension, conference):
    with a.conference_extension(conference, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(response.item, has_entries(
            conference=has_entries(id=conference['id'],
                                   name=conference['name'])
        ))


@fixtures.conference()
@fixtures.extension()
def test_edit_context_to_incall_when_associated(conference, extension):
    with a.conference_extension(conference, extension):
        response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
        response.assert_status(400)


@fixtures.conference()
@fixtures.extension()
def test_delete_conference_when_conference_and_extension_associated(conference, extension):
    with a.conference_extension(conference, extension, check=False):
        response = confd.conferences(conference['id']).delete()
        response.assert_deleted()


def test_delete_extension_when_conference_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
