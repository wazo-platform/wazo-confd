# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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
from ..test_api import scenarios as s
from ..test_api import errors as e
from ..test_api import fixtures
from ..test_api import associations as a
from xivo_test_helpers.confd.config import INCALL_CONTEXT
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
    fake_conference_extension = confd.conferences(conference['id']).extensions(extension['id']).delete
    fake_conference = confd.conferences(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.conferences(conference['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_conference, 'Conference'
    yield s.check_resource_not_found, fake_extension, 'Extension'
    yield s.check_resource_not_found, fake_conference_extension, 'ConferenceExtension'


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
        response.assert_match(400, e.resource_associated('Conference', 'Extension'))


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
