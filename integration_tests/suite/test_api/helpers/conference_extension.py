# -*- coding: UTF-8 -*-

# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
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


from test_api import confd


def associate(conference_id, extension_id, check=True):
    response = confd.conferences(conference_id).extensions(extension_id).put()
    if check:
        response.assert_ok()


def dissociate(conference_id, extension_id, check=True):
    response = confd.conferences(conference_id).extensions(extension_id).delete()
    if check:
        response.assert_ok()
