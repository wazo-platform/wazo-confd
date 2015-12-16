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

from test_api import errors as e
from test_api import confd
from test_api import fixtures as f
from test_api import associations as a

from hamcrest import assert_that, has_entries


@f.line_sip()
@f.extension()
def test_associate_line_and_extension(line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    response = confd.lines(line['id']).extension.post(extension_id=extension['id'])
    response.assert_created('lines', 'extension')
    assert_that(response.item, expected)


@f.user()
@f.line_sip()
@f.extension()
def test_associate_user_line_extension(user, line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    with a.user_line(user, line, check=False):
        response = confd.lines(line['id']).extension.post(extension_id=extension['id'])
        response.assert_created('lines', 'extension')
        assert_that(response.item, expected)


@f.user()
@f.line_sip()
@f.extension()
def test_dissociate_user_line_extension(user, line, extension):
    with a.user_line(user, line), a.line_extension(line, extension, check=False):
        response = confd.lines(line['id']).extension.delete()
        response.assert_deleted()


@f.line_sip()
@f.extension()
def test_get_line_from_extension(line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    with a.line_extension(line, extension):
        response = confd.lines(line['id']).extension.get()
        assert_that(response.item, expected)


@f.line_sip()
@f.extension()
def test_get_extension_from_line(line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    with a.line_extension(line, extension):
        response = confd.extensions(extension['id']).line.get()
        assert_that(response.item, expected)


@f.line_sip()
@f.extension()
@f.device()
def test_dissociate_when_line_associated_to_device(line, extension, device):
    with a.line_extension(line, extension), a.line_device(line, device):
        response = confd.lines(line['id']).extension.delete()
        response.assert_match(400, e.resource_associated('Line', 'Device'))
