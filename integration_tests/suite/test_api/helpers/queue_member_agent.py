# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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


def associate(queue_id, agent_id, **kwargs):
    check = kwargs.pop('check', True)
    kwargs['agent_id'] = agent_id
    response = confd.queues(queue_id).members.agents.post(**kwargs)
    if check:
        response.assert_ok()


def dissociate(queue_id, agent_id, **kwargs):
    check = kwargs.get('check', True)
    response = confd.queues(queue_id).members.agents(agent_id).delete()
    if check:
        response.assert_ok()
