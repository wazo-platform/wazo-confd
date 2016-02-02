# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from __future__ import unicode_literals


import re

from test_api import config
from test_api import confd
from test_api import fixtures
from test_api import scenarios as s
from test_api import errors as e
from test_api import associations as a

from hamcrest import assert_that, has_entries, none, has_length, has_items, \
    has_entry, contains


def test_get_errors():
    fake_line_get = confd.lines(999999).get
    yield s.check_resource_not_found, fake_line_get, 'Line'


def test_post_errors():
    empty_post = confd.lines.post
    line_post = confd.lines(context=config.CONTEXT).post

    yield s.check_missing_required_field_returns_error, empty_post, 'context'
    yield s.check_bogus_field_returns_error, empty_post, 'context', 123
    yield s.check_bogus_field_returns_error, line_post, 'provisioning_code', 123456
    yield s.check_bogus_field_returns_error, line_post, 'provisioning_code', 'number'
    yield s.check_bogus_field_returns_error, line_post, 'position', 'one'


@fixtures.line()
@fixtures.sip()
def test_put_errors(line, sip):
    line_put = confd.lines(line['id']).put

    yield s.check_missing_required_field_returns_error, line_put, 'context'
    yield s.check_bogus_field_returns_error, line_put, 'context', 123
    yield s.check_bogus_field_returns_error, line_put, 'provisioning_code', 123456
    yield s.check_bogus_field_returns_error, line_put, 'provisioning_code', 'number'
    yield s.check_bogus_field_returns_error, line_put, 'provisioning_code', None
    yield s.check_bogus_field_returns_error, line_put, 'position', 'one'
    yield s.check_bogus_field_returns_error, line_put, 'position', None

    with a.line_endpoint_sip(line, sip):
        yield s.check_bogus_field_returns_error, line_put, 'caller_id_num', 'number'
        yield s.check_bogus_field_returns_error, line_put, 'caller_id_name', 123456


@fixtures.line()
def test_delete_errors(line):
    line_url = confd.lines(line['id'])
    line_url.delete()
    yield s.check_resource_not_found, line_url.get, 'Line'


@fixtures.line(context=config.CONTEXT)
def test_get(line):
    expected = has_entries({'context': config.CONTEXT,
                            'position': 1,
                            'device_slot': 1,
                            'name': none(),
                            'protocol': none(),
                            'device_id': none(),
                            'caller_id_name': none(),
                            'caller_id_num': none(),
                            'provisioning_code': has_length(6),
                            'provisioning_extension': has_length(6)}
                           )

    response = confd.lines(line['id']).get()
    assert_that(response.item, expected)


@fixtures.line()
@fixtures.line()
def test_search(line1, line2):
    expected = has_items(has_entry('id', line1['id']),
                         has_entry('id', line2['id']))

    response = confd.lines.get()
    assert_that(response.items, expected)

    expected = contains(has_entry('id', line1['id']))

    response = confd.lines.get(search=line1['provisioning_code'])
    assert_that(response.items, expected)


def test_create_line_with_fake_context():
    response = confd.lines.post(context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


def test_create_line_with_minimal_parameters():
    expected = has_entries({'context': config.CONTEXT,
                            'position': 1,
                            'device_slot': 1,
                            'name': none(),
                            'protocol': none(),
                            'device_id': none(),
                            'caller_id_name': none(),
                            'caller_id_num': none(),
                            'provisioning_code': has_length(6),
                            'provisioning_extension': has_length(6)}
                           )

    response = confd.lines.post(context=config.CONTEXT)

    response.assert_created('lines')
    assert_that(response.item, expected)


def test_create_line_with_all_parameters():
    expected = has_entries({'context': config.CONTEXT,
                            'position': 2,
                            'device_slot': 2,
                            'name': none(),
                            'protocol': none(),
                            'device_id': none(),
                            'caller_id_name': none(),
                            'caller_id_num': none(),
                            'provisioning_code': "887865",
                            'provisioning_extension': "887865"}
                           )

    response = confd.lines.post(context=config.CONTEXT,
                                position=2,
                                provisioning_code="887865")

    assert_that(response.item, expected)


def test_create_line_with_caller_id_raises_error():
    response = confd.lines.post(context=config.CONTEXT,
                                caller_id_name="Jôhn Smîth",
                                caller_id_num="1000")

    response.assert_status(400)


@fixtures.line(provisioning_code="135246")
def test_create_line_with_provisioning_code_already_taken(line):
    response = confd.lines.post(context=config.CONTEXT,
                                provisioning_code="135246")
    response.assert_match(400, re.compile("provisioning_code"))


@fixtures.line()
def test_update_line_with_fake_context(line):
    response = confd.lines(line['id']).put(context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


@fixtures.line()
@fixtures.context()
def test_update_all_parameters_on_line(line, context):
    url = confd.lines(line['id'])
    expected = has_entries({'context': context['name'],
                            'position': 2,
                            'caller_id_name': none(),
                            'caller_id_num': none(),
                            'provisioning_code': '243546'})

    response = url.put(context=context['name'],
                       position=2,
                       provisioning_code='243546')
    response.assert_updated()

    response = url.get()
    assert_that(response.item, expected)


@fixtures.line()
def test_update_caller_id_on_line_without_endpoint_raises_error(line):
    response = confd.lines(line['id']).put(caller_id_name="Jôhn Smîth",
                                           caller_id_num="1000")
    response.assert_status(400)


@fixtures.line()
def test_delete_line(line):
    response = confd.lines(line['id']).delete()
    response.assert_deleted()
