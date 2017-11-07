# -*- coding: utf-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
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
import datetime

from hamcrest import (assert_that,
                      contains,
                      contains_inanyorder,
                      equal_to,
                      empty,
                      has_entry,
                      has_entries,
                      has_item,
                      is_not,
                      none,
                      not_)

from ..test_api import associations as a
from ..test_api import scenarios as s
from ..test_api import helpers as h
from ..test_api import errors as e
from ..test_api import fixtures
from xivo_test_helpers.confd.config import CONTEXT
from . import confd, provd

outside_range_regex = re.compile(r"Extension '(\d+)' is outside of range for context '([\w_-]+)'")

FAKE_ID = 999999999


def test_search_errors():
    url = confd.extensions.get
    for check in s.search_error_checks(url):
        yield check


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
    url = confd.extensions(extension['id']).put
    for check in error_checks(url):
        yield check


def test_delete_errors():
    url = confd.extensions(FAKE_ID).delete
    yield s.check_resource_not_found, url, 'Extension'


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'exten', None
    yield s.check_bogus_field_returns_error, url, 'exten', True
    yield s.check_bogus_field_returns_error, url, 'exten', 'ABC123'
    yield s.check_bogus_field_returns_error, url, 'exten', 'XXXX'
    yield s.check_bogus_field_returns_error, url, 'exten', {}
    yield s.check_bogus_field_returns_error, url, 'exten', []
    yield s.check_bogus_field_returns_error, url, 'context', None
    yield s.check_bogus_field_returns_error, url, 'context', True
    yield s.check_bogus_field_returns_error, url, 'context', {}
    yield s.check_bogus_field_returns_error, url, 'context', []


@fixtures.extension()
def test_get(extension):
    response = confd.extensions(extension['id']).get()
    assert_that(response.item, has_entries(exten=extension['exten'],
                                           context=extension['context'],
                                           commented=False,
                                           incall=none(),
                                           outcall=none(),
                                           lines=empty(),
                                           conference=none(),
                                           parking_lot=none()))


def test_create_minimal_parameters():
    exten = h.extension.find_available_exten(CONTEXT)

    response = confd.extensions.post(exten=exten,
                                     context=CONTEXT)
    response.assert_created('extensions')

    assert_that(response.item, has_entries(exten=exten,
                                           context=CONTEXT,
                                           commented=False))


def test_create_with_commented_parameter():
    exten = h.extension.find_available_exten(CONTEXT)

    response = confd.extensions.post(exten=exten,
                                     context=CONTEXT,
                                     commented=True)
    response.assert_created('extensions')

    assert_that(response.item, has_entries(exten=exten,
                                           context=CONTEXT,
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


@fixtures.context(incall_ranges=[{'start': '4185550000', 'end': '4185559999', 'did_length': 4}])
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


def test_create_pattern():
    response = confd.extensions.post(exten='_XXXX',
                                     context='default')
    response.assert_created('extensions')


@fixtures.context()
def test_create_2_extensions_same_exten_different_context(context):
    exten = h.extension.find_available_exten(CONTEXT)

    response = confd.extensions.post(exten=exten, context=CONTEXT)
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
def test_edit_pattern(extension):
    response = confd.extensions(extension['id']).put(exten='_X21',
                                                     context='default')
    response.assert_updated()


@fixtures.extension()
@fixtures.context()
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


@fixtures.user()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.extension()
@fixtures.extension()
@fixtures.device()
@fixtures.device()
def test_edit_extension_then_funckeys_updated(user1, user2, user3,
                                              line_sip1, line_sip2, line_sip3,
                                              extension1, extension2, extension3,
                                              device1, device2):
    timestamp = datetime.datetime.utcnow()
    with a.line_extension(line_sip1, extension1), a.user_line(user1, line_sip1), a.line_device(line_sip1, device1), \
            a.line_extension(line_sip2, extension2), a.user_line(user2, line_sip2), a.line_device(line_sip2, device2), \
            a.line_extension(line_sip3, extension3), a.user_line(user3, line_sip3):
        device2_updated_count = provd.updated_count(device2['id'], timestamp)

        destination = {'type': 'user', 'user_id': user3['id']}
        confd.users(user1['id']).funckeys(1).put(destination=destination).assert_updated()

        confd.extensions(extension3['id']).put(exten='1033').assert_updated()

        config = provd.configs.get(device1['id'])
        assert_that(config['raw_config']['funckeys']['1']['value'], equal_to('1033'))
        assert_that(provd.updated_count(device2['id'], timestamp), equal_to(device2_updated_count))


@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.extension()
@fixtures.device()
def test_edit_extension_with_no_change_device_not_updated(user1, user2,
                                                          line_sip1, line_sip2,
                                                          extension1, extension2,
                                                          device):
    timestamp = datetime.datetime.utcnow()
    with a.line_extension(line_sip1, extension1), a.user_line(user1, line_sip1), a.line_device(line_sip1, device), \
            a.line_extension(line_sip2, extension2), a.user_line(user2, line_sip2):
        destination = {'type': 'user', 'user_id': user2['id']}
        confd.users(user1['id']).funckeys(1).put(destination=destination).assert_updated()

        device_updated_count = provd.updated_count(device['id'], timestamp)

        confd.extensions(extension2['id']).put(exten=extension2['exten']).assert_updated()

        assert_that(provd.updated_count(device['id'], timestamp), equal_to(device_updated_count))


@fixtures.extension(exten='4999', context='default')
@fixtures.extension(exten='9999', context='from-extern')
def test_search(extension, hidden):
    url = confd.extensions
    searches = {'exten': '499',
                'context': 'fault'}

    for field, term in searches.items():
        yield check_search, url, extension, hidden, field, term


def check_search(url, extension, hidden, field, term):
    response = url.get(search=term)

    expected_extension = has_item(has_entry(field, extension[field]))
    hidden_extension = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, expected_extension)
    assert_that(response.items, hidden_extension)

    response = url.get(**{field: extension[field]})

    expected_extension = has_item(has_entry('id', extension['id']))
    hidden_extension = is_not(has_item(has_entry('id', hidden['id'])))
    assert_that(response.items, expected_extension)
    assert_that(response.items, hidden_extension)


@fixtures.extension(exten='9998', context='from-extern')
@fixtures.extension(exten='9999', context='to-extern')
def test_sorting_offset_limit(extension1, extension2):
    url = confd.extensions.get
    yield s.check_sorting, url, extension1, extension2, 'exten', '999'
    yield s.check_sorting, url, extension1, extension2, 'context', 'extern'

    yield s.check_offset, url, extension1, extension2, 'exten', '999'
    yield s.check_offset_legacy, url, extension1, extension2, 'exten', '999'

    yield s.check_limit, url, extension1, extension2, 'exten', '999'


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
