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

from test_api.helpers.line_extension import line_and_extension_associated as l_e_association
from test_api.helpers.user_line import user_and_line_associated as u_l_association
from test_api.helpers.line_device import line_and_device_associated as l_d_association
from test_api import errors as e
from test_api import confd
from test_api import fixtures as f

from hamcrest import assert_that, has_entries


@f.line()
@f.extension()
def test_associate_line_and_extension(line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    response = confd.lines(line['id']).extension.post(extension_id=extension['id'])
    assert_that(response.item, expected)


@f.user()
@f.line()
@f.extension()
def test_associate_user_line_extension(user, line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    with u_l_association(user, line, check=False):
        response = confd.lines(line['id']).extension.post(extension_id=extension['id'])
        assert_that(response.item, expected)


@f.user()
@f.line()
@f.extension()
def test_dissociate_user_line_extension(user, line, extension):
    with u_l_association(user, line), l_e_association(line, extension, check=False):
        response = confd.lines(line['id']).extension.delete()
        response.assert_ok()


@f.line()
@f.extension()
def test_get_line_from_extension(line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    with l_e_association(line, extension):
        response = confd.lines(line['id']).extension.get()
        assert_that(response.item, expected)


@f.line()
@f.extension()
def test_get_extension_from_line(line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    with l_e_association(line, extension):
        response = confd.extensions(extension['id']).line.get()
        assert_that(response.item, expected)


@f.line()
@f.extension()
@f.device()
def test_dissociate_when_line_associated_to_device(line, extension, device):
    with l_e_association(line, extension), l_d_association(line, device):
        response = confd.lines(line['id']).extension.delete()
        response.assert_status(400, e.resource_associated('Line', 'Device'))
