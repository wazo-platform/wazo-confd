# -*- coding: UTF-8 -*-

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


from test_api import confd


def associate(outcall_id, trunk_ids, check=True):
    trunks = [{'id': trunk_id} for trunk_id in trunk_ids]
    response = confd.outcalls(outcall_id).trunks.put(trunks=trunks)
    if check:
        response.assert_ok()


def dissociate(outcall_id, check=True):
    response = confd.outcalls(outcall_id).trunks.put(trunks=[])
    if check:
        response.assert_ok()
