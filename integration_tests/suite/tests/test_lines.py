# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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


import re

from test_api import config
from test_api import confd
from test_api import fixtures
from test_api import scenarios as s
from test_api import errors as e

from hamcrest import assert_that, has_entries, none, has_length


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
    yield s.check_bogus_field_returns_error, line_post, 'position', '1'
    yield s.check_bogus_field_returns_error, line_post, 'caller_num', 'number'


@fixtures.line()
def test_put_errors(line):
    line_put = confd.lines(line['id']).put

    yield s.check_missing_required_field_returns_error, line_put, 'context'
    yield s.check_bogus_field_returns_error, line_put, 'context', 123
    yield s.check_bogus_field_returns_error, line_put, 'provisioning_code', 123456
    yield s.check_bogus_field_returns_error, line_put, 'provisioning_code', 'number'
    yield s.check_bogus_field_returns_error, line_put, 'position', '1'
    yield s.check_bogus_field_returns_error, line_put, 'caller_num', 'number'


@fixtures.line()
def test_delete_errors(line):
    line_url = confd.lines(line['id'])
    line_url.delete()
    yield s.check_resource_not_found, line_url.get, 'Line'


def test_create_line_with_fake_context():
    response = confd.lines_sip.post(context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


def test_create_line_with_minimal_parameters():
    expected = has_entries({'context': config.CONTEXT,
                            'position': 1,
                            'device_slot': 1,
                            'name': none(),
                            'protocol': none(),
                            'device_id': none(),
                            'caller_name': none(),
                            'caller_num': none(),
                            'provisioning_code': has_length(6),
                            'provisioning_extension': has_length(6)}
                           )

    response = confd.lines.post(context=config.CONTEXT)
    assert_that(response.item, expected)


def test_create_line_with_all_parameters():
    expected = has_entries({'context': config.CONTEXT,
                            'position': 2,
                            'device_slot': 2,
                            'name': none(),
                            'protocol': none(),
                            'device_id': none(),
                            'caller_name': u"Fodé Sanderson",
                            'caller_num': "1000",
                            'provisioning_code': "987654",
                            'provisioning_extension': "987654"}
                           )

    response = confd.lines.post(context=config.CONTEXT,
                                position=2,
                                caller_name=u"Fodé Sanderson",
                                caller_num="1000",
                                provisioning_code="987654")

    assert_that(response.item, expected)


@fixtures.line(provisioning_code="123456")
def test_create_line_with_provisioning_code_already_taken(line):
    response = confd.lines.post(context=config.CONTEXT,
                                provisioning_code="123456")
    response.assert_status(400, re.compile("provisioning_code"))


@fixtures.line()
def test_update_line_with_fake_context(line):
    response = confd.lines_sip(line['id']).put(context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


@fixtures.line(caller_name=u"Fodé Sanderson", caller_num="1000")
@fixtures.context()
def test_update_all_parameters_on_line(line, context):
    url = confd.lines(line['id'])
    expected = has_entries({'context': context['name'],
                            'position': 2,
                            'caller_name': u"Mamàsta Michel",
                            'caller_num': "2000",
                            'provisioning_code': '234567'})

    response = url.put(context=context['name'],
                       position=2,
                       caller_name=u"Mamàsta Michel",
                       caller_num="2000",
                       provisioning_code='234567')
    response.assert_ok()

    response = url.get()
    assert_that(response.item, expected)


@fixtures.line(caller_name=u"Fodé Sanderson", caller_num="1000")
def test_update_null_parameters(line):
    url = confd.lines(line['id'])
    expected = has_entries({'caller_name': None,
                            'caller_num': None})

    response = url.put(caller_name=None,
                       caller_num=None)
    response.assert_ok()

    response = url.get()
    assert_that(response.item, expected)


@fixtures.line()
def test_delete_line(line):
    response = confd.lines(line['id']).delete()
    response.assert_ok()
