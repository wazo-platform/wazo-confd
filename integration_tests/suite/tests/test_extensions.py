# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import re

from hamcrest import assert_that
from hamcrest import contains
from hamcrest import contains_inanyorder

from test_api import confd
from test_api import scenarios as s
from test_api import errors as e
from test_api import fixtures
from test_api.helpers.extension import generate_extension

outside_range_regex = re.compile(r"Extension '(\d+)' is outside of range for context '([\w_-]+)'")


REQUIRED = ['exten', 'context']

BOGUS = [('exten', 123, 'unicode string'),
         ('context', 123, 'unicode string'),
         ('commented', 'true', 'boolean')]


class TestExtensionResource(s.GetScenarios, s.CreateScenarios, s.EditScenarios, s.DeleteScenarios):

    url = "/extensions"
    resource = "Extension"
    required = REQUIRED
    bogus_fields = BOGUS

    def create_resource(self):
        extension = generate_extension()
        return extension['id']


def test_alphanumeric_extension():
    error = e.wrong_type('exten', 'numeric string')
    response = confd.extensions.post(context='default',
                                     exten='ABC123')
    response.assert_match(400, error)


@fixtures.extension()
def test_create_2_extensions_with_same_exten(extension):
    response = confd.extensions.post(context=extension['context'],
                                     exten=extension['exten'])
    response.assert_match(400, e.resource_exists('Extension'))


def test_create_extension_with_fake_context():
    response = confd.extensions.post(exten='1234',
                                     context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


def test_create_extension_outside_context_range():
    response = confd.extensions.post(exten='999999999',
                                     context='default')
    response.assert_match(400, outside_range_regex)


@fixtures.extension()
def test_edit_extension_outside_context_range(extension):
    response = confd.extensions(extension['id']).put(exten='999999999',
                                                     context='default')
    response.assert_match(400, outside_range_regex)


@fixtures.extension()
def test_edit_extension_with_fake_context(extension):
    response = confd.extensions(extension['id']).put(exten='1234',
                                                     context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


@fixtures.extension(exten='1001', context='default')
@fixtures.extension(exten='1001', context='from-extern')
@fixtures.extension(exten='1002', context='from-extern')
def test_search_extensions(extension1, extension2, extension3):
    expected = contains_inanyorder(extension1, extension2)

    response = confd.extensions.get(search='1001')

    assert_that(response.items, expected)


@fixtures.extension(exten='1001', context='default')
@fixtures.extension(exten='1001', context='from-extern')
@fixtures.extension(exten='1002', context='from-extern')
def test_search_extensions_in_context(extension1, extension2, extension3):
    expected = contains(extension2)

    response = confd.extensions.get(search='1001', context='from-extern')

    assert_that(response.items, expected)


@fixtures.extension(exten='1001', context='default')
@fixtures.extension(exten='1001', context='from-extern')
@fixtures.extension(exten='1002', context='from-extern')
def test_search_list_extensions_in_context(extension1, extension2, extension3):
    expected = contains(extension2, extension3)

    response = confd.extensions.get(context='from-extern')

    assert_that(response.items, expected)
