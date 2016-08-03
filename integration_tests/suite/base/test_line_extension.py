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

from test_api.helpers.line_sip import generate_line, delete_line
from test_api.helpers.extension import generate_extension, delete_extension
from test_api import scenarios as s
from test_api import errors as e
from test_api import associations as a
from test_api import helpers as h
from test_api import confd
from test_api import db
from test_api import fixtures
from test_api import config

from hamcrest import assert_that
from hamcrest import contains
from hamcrest import empty
from hamcrest import has_entries
from hamcrest import has_item

import re


FAKE_ID = 999999999

no_line_associated_regex = re.compile(r"Extension with id=\d+ does not have a line")
no_user_associated_regex = re.compile(r"line with id \d+ is not associated to a user")
already_associated_regex = re.compile(r"line with id \d+ already has an extension with a context of type 'internal'")


class TestLineExtensionCollectionAssociation(s.AssociationScenarios,
                                             s.DissociationCollectionScenarios,
                                             s.AssociationGetCollectionScenarios):

    left_resource = "Line"
    right_resource = "Extension"

    def create_resources(self):
        line = generate_line()
        extension = generate_extension()
        return line['id'], extension['id']

    def delete_resources(self, line_id, extension_id):
        delete_line(line_id)
        delete_extension(extension_id)

    def associate_resources(self, line_id, extension_id):
        return confd.lines(line_id).extensions.post(extension_id=extension_id)

    def dissociate_resources(self, line_id, extension_id):
        return confd.lines(line_id).extensions(extension_id).delete()

    def get_association(self, line_id, extension_id):
        return confd.lines(line_id).extensions.get()


class TestLineExtensionAssociation(s.AssociationScenarios, s.DissociationScenarios, s.AssociationGetScenarios):

    left_resource = "Line"
    right_resource = "Extension"

    def create_resources(self):
        line = generate_line()
        extension = generate_extension()
        return line['id'], extension['id']

    def delete_resources(self, line_id, extension_id):
        delete_line(line_id)
        delete_extension(extension_id)

    def associate_resources(self, line_id, extension_id):
        return confd.lines(line_id).extension.post(extension_id=extension_id)

    def dissociate_resources(self, line_id, extension_id):
        return confd.lines(line_id).extension.delete()

    def get_association(self, line_id, extension_id):
        return confd.lines(line_id).extension.get()


@fixtures.line()
@fixtures.extension()
def test_associate_errors(line, extension):
    fake_line = confd.lines(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.lines(line['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.line_sip()
def test_get_associations_when_not_associated(line):
    response = confd.lines(line['id']).extensions.get()
    assert_that(response.items, contains())


@fixtures.line_sip()
@fixtures.extension()
def test_get_line_from_extension_when_not_associated(line, extension):
    response = confd.extensions(extension['id']).line.get()
    response.assert_match(404, e.not_found('LineExtension'))


@fixtures.line_sip()
@fixtures.extension(context=config.INCALL_CONTEXT)
def test_get_line_from_incall_when_not_associated(line, incall):
    response = confd.extensions(incall['id']).line.get()
    response.assert_match(404, e.not_found('LineExtension'))


def test_get_line_from_fake_extension():
    response = confd.extensions(FAKE_ID).line.get()
    response.assert_match(404, e.not_found('Extension'))


@fixtures.line_sip()
@fixtures.extension()
def test_associate_line_and_internal_extension(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_updated()

    response = confd.lines(line['id']).extensions.get()
    assert_that(response.items, contains(has_entries({'line_id': line['id'],
                                                      'extension_id': extension['id']})))


@fixtures.extension(context='from-extern')
@fixtures.line_sip()
def test_associate_incall_to_line_without_user(incall, line):
    response = confd.lines(line['id']).extensions(incall['id']).put()
    response.assert_match(400, e.missing_association('Line', 'User'))


@fixtures.extension()
@fixtures.extension()
@fixtures.line_sip()
def test_associate_two_internal_extensions_to_same_line(first_extension, second_extension, line):
    response = confd.lines(line['id']).extensions(first_extension['id']).put()
    response.assert_updated()

    response = confd.lines(line['id']).extensions(second_extension['id']).put()
    response.assert_match(400, e.resource_associated('Line', 'Extension'))


@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_extension(extension, line1, line2, line3):
    response = confd.lines(line1['id']).extensions.post(extension_id=extension['id'])
    response.assert_created('lines', 'extensions')

    response = confd.lines(line2['id']).extensions.post(extension_id=extension['id'])
    response.assert_created('lines', 'extensions')

    response = confd.lines(line3['id']).extensions.post(extension_id=extension['id'])
    response.assert_created('lines', 'extensions')


@fixtures.user()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_extension_with_same_user(user, extension, line1, line2):
    with a.user_line(user, line1), a.user_line(user, line2):
        response = confd.lines(line1['id']).extensions.post(extension_id=extension['id'])
        response.assert_created('lines', 'extensions')

        response = confd.lines(line2['id']).extensions.post(extension_id=extension['id'])
        response.assert_created('lines', 'extensions')


@fixtures.user()
@fixtures.user()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_extension_with_different_user(user1, user2, extension, line1, line2):
    with a.user_line(user1, line1), a.user_line(user2, line2):
        response = confd.lines(line1['id']).extensions.post(extension_id=extension['id'])
        response.assert_created('lines', 'extensions')

        response = confd.lines(line2['id']).extensions.post(extension_id=extension['id'])
        response.assert_match(400, e.resource_associated('User', 'Line'))


@fixtures.user()
@fixtures.extension()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_multi_extensions_with_same_user(user, extension1, extension2, line1, line2):
    with a.user_line(user, line1), a.user_line(user, line2):
        response = confd.lines(line1['id']).extensions.post(extension_id=extension1['id'])
        response.assert_created('lines', 'extensions')

        response = confd.lines(line2['id']).extensions.post(extension_id=extension2['id'])
        response.assert_created('lines', 'extensions')


@fixtures.line_sip()
def test_associate_line_to_extension_already_associated_to_other_resource(line):
    with db.queries() as queries:
        queries.insert_queue(number='1234')

    extension_id = confd.extensions.get(exten='1234').items[0]['id']

    response = confd.lines(line['id']).extensions(extension_id).put()
    response.assert_match(400, e.resource_associated('Extension', 'queue'))


@fixtures.line()
@fixtures.extension()
def test_associate_line_without_endpoint(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_match(400, e.missing_association('Line', 'Endpoint'))


@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_associate_line_with_endpoint(line, sip, extension):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_updated()
        response = confd.lines(line['id']).extensions.get()
        assert_that(response.items, contains(has_entries({'line_id': line['id'],
                                                          'extension_id': extension['id']})))


@fixtures.line_sip()
@fixtures.extension()
def test_dissociate_line_and_extension(line, extension):
    with a.line_extension(line, extension, check=False):
        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.line_sip()
@fixtures.extension()
def test_delete_extension_associated_to_line(line, extension):
    with a.line_extension(line, extension):
        response = confd.extensions(extension['id']).delete()
        response.assert_match(400, e.resource_associated('Extension', 'Line'))


@fixtures.line_sip()
@fixtures.extension()
def test_get_line_extension(line, extension):
    expected = has_item(has_entries(line_id=line['id'],
                                    extension_id=extension['id']))

    with a.line_extension(line, extension):
        response = confd.lines(line['id']).extensions.get()
        assert_that(response.items, expected)


@fixtures.line_sip()
@fixtures.extension()
def test_get_line_extension_after_dissociation(line, extension):
    h.line_extension.associate(line['id'], extension['id'])
    h.line_extension.dissociate(line['id'], extension['id'])

    response = confd.lines(line['id']).extensions.get()
    assert_that(response.items, empty())
