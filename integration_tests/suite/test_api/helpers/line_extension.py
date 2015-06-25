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

from contextlib import contextmanager

from test_api import confd


def associate(line_id, extension_id):
    response = confd.lines(line_id).extensions.post(extension_id=extension_id)
    response.assert_ok()


def dissociate(line_id, extension_id):
    response = confd.lines(line_id).extensions(extension_id).delete()
    response.assert_ok()


@contextmanager
def line_and_extension_associated(line, extension):
    associate(line['id'], extension['id'])
    yield
    dissociate(line['id'], extension['id'])
