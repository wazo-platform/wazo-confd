# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
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
from hamcrest import has_entries
from hamcrest import has_item
from hamcrest import not_

from test_api import confd
from test_api import config
from test_api import scenarios as s
from test_api import helpers as h
from test_api import errors as e
from test_api import fixtures

outside_range_regex = re.compile(r"Extension '(\d+)' is outside of range for context '([\w_-]+)'")

FAKE_ID = 999999999


def test_alphanumeric_extension():
    url = confd.extensions(context='default').post
    yield s.check_bogus_field_returns_error, url, 'exten', 'ABC123'


def test_get_errors():
    url = confd.extensions(FAKE_ID).get
    yield s.check_resource_not_found, url, 'Extension'


@fixtures.extension()
def test_post_errors(extension):
    url = confd.extensions.post
    for check in error_checks(url):
        yield check


@fixtures.extension()
def test_put_errors(extension):
    url = confd.extensions(extension['id'],
                           exten=extension['exten'],
                           context=extension['context']).put
    for check in error_checks(url):
        yield check


@fixtures.extension()
def test_delete_errors(extension):
    url = confd.extensions(extension['id'])
    url.delete()
    yield s.check_resource_not_found, url.get, 'Extension'


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'exten', None
    yield s.check_bogus_field_returns_error, url, 'context', None


@fixtures.extension()
def test_get(extension):
    response = confd.extensions(extension['id']).get()
    assert_that(response.item, has_entries(exten=extension['exten'],
                                           context=extension['context'],
                                           commented=False))


def test_create_minimal_parameters():
    exten = h.extension.find_available_exten(config.CONTEXT)

    response = confd.extensions.post(exten=exten,
                                     context=config.CONTEXT)
    response.assert_created('extensions')

    assert_that(response.item, has_entries(exten=exten,
                                           context=config.CONTEXT,
                                           commented=False))


def test_create_with_commented_parameter():
    exten = h.extension.find_available_exten(config.CONTEXT)

    response = confd.extensions.post(exten=exten,
                                     context=config.CONTEXT,
                                     commented=True)
    response.assert_created('extensions')

    assert_that(response.item, has_entries(exten=exten,
                                           context=config.CONTEXT,
                                           commented=True))


def test_create_extension_in_different_ranges():
    # user range
    yield create_in_range, '1100', 'default'
    # group range
    yield create_in_range, '2000', 'default'
    # queue range
    yield create_in_range, '3000', 'default'
    # conference range
    yield create_in_range, '4000', 'default'
    # incall range
    yield create_in_range, '3954', 'from-extern'


def create_in_range(exten, context):
    response = confd.extensions.create(exten=exten, context=context)
    response.assert_created('extensions')


@fixtures.context(start='4185550000', end='4185559999', didlength=4)
def test_create_extension_in_context_with_did_length(context):
    response = confd.extensions.create(exten='1000', context=context['name'])
    response.assert_created('extensions')


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


@fixtures.context(start='1000', end='9999')
def test_create_2_extensions_same_exten_different_context(context):
    exten = h.extension.find_available_exten(config.CONTEXT)

    response = confd.extensions.post(exten=exten, context=config.CONTEXT)
    response.assert_created('extensions')

    response = confd.extensions.post(exten=exten, context=context['name'])
    response.assert_created('extensions')


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


@fixtures.extension()
@fixtures.context(start='1000', end='9999')
def test_update_required_parameters(extension, context):
    exten = h.extension.find_available_exten(context['name'])
    url = confd.extensions(extension['id'])

    response = url.put(exten=exten,
                       context=context['name'])
    response.assert_updated()

    assert_that(url.get().item, has_entries(exten=exten,
                                            context=context['name']))


@fixtures.extension(commented=False)
def test_update_additional_parameters(extension1):
    url = confd.extensions(extension1['id'])
    url.put(commented=True).assert_updated()
    assert_that(url.get().item, has_entries(commented=True))


def test_search_extensions():
    exten = h.extension.find_available_exten('default')
    exten2 = h.extension.find_available_exten('from-extern')

    with fixtures.extension(exten=exten, context='default') as extension1, \
            fixtures.extension(exten=exten, context='from-extern') as extension2, \
            fixtures.extension(exten=exten2, context='from-extern'):

        expected = contains_inanyorder(extension1, extension2)
        response = confd.extensions.get(search=exten)
        assert_that(response.items, expected)


def test_search_extensions_in_context():
    exten = h.extension.find_available_exten('default')
    exten2 = h.extension.find_available_exten('from-extern')

    with fixtures.extension(exten=exten, context='default'), \
            fixtures.extension(exten=exten, context='from-extern') as extension2, \
            fixtures.extension(exten=exten2, context='from-extern'):

        expected = contains(extension2)
        response = confd.extensions.get(search=exten, context='from-extern')
        assert_that(response.items, expected)


def test_search_list_extensions_in_context():
    exten = h.extension.find_available_exten('default')
    exten2 = h.extension.find_available_exten('from-extern')

    with fixtures.extension(exten=exten, context='default'), \
            fixtures.extension(exten=exten, context='from-extern') as extension2, \
            fixtures.extension(exten=exten2, context='from-extern') as extension3:

        expected = contains_inanyorder(extension2, extension3)
        response = confd.extensions.get(context='from-extern')
        assert_that(response.items, expected)


@fixtures.extension(context='default')
@fixtures.extension(context='from-extern')
def test_search_extensions_by_type(internal, incall):
    expected_internal = has_item(has_entries(id=internal['id']))
    expected_incall = has_item(has_entries(id=incall['id']))

    response = confd.extensions.get(type="internal")
    assert_that(response.items, expected_internal)
    assert_that(response.items, not_(expected_incall))

    response = confd.extensions.get(type="incall")
    assert_that(response.items, not_(expected_internal))
    assert_that(response.items, expected_incall)


@fixtures.extension()
def test_delete(extension):
    response = confd.extensions(extension['id']).delete()
    response.assert_deleted()
