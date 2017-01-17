# -*- coding: UTF-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
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

from test_api import helpers as h


@contextmanager
def user_line(user, line, check=True):
    h.user_line.associate(user['id'], line['id'], check)
    yield
    h.user_line.dissociate(user['id'], line['id'], check)


@contextmanager
def user_voicemail(user, voicemail, check=True):
    h.user_voicemail.associate(user['id'], voicemail['id'], check)
    yield
    h.user_voicemail.dissociate(user['id'], voicemail['id'], check)


@contextmanager
def user_cti_profile(user, cti_profile, check=True):
    h.user_cti_profile.associate(user['id'], cti_profile['id'])
    yield
    h.user_cti_profile.dissociate(user['id'], cti_profile['id'])


@contextmanager
def line_extension(line, extension, check=True):
    h.line_extension.associate(line['id'], extension['id'], check)
    yield
    h.line_extension.dissociate(line['id'], extension['id'], check)


@contextmanager
def line_device(line, device, check=True):
    h.line_device.associate(line['id'], device['id'], check)
    yield
    h.line_device.dissociate(line['id'], device['id'], check)


@contextmanager
def line_endpoint_sip(line, sip, check=True):
    h.line_endpoint_sip.associate(line['id'], sip['id'], check)
    yield
    h.line_endpoint_sip.dissociate(line['id'], sip['id'], check)


@contextmanager
def line_endpoint_sccp(line, sccp, check=True):
    h.line_endpoint_sccp.associate(line['id'], sccp['id'], check)
    yield
    h.line_endpoint_sccp.dissociate(line['id'], sccp['id'], check)


@contextmanager
def line_endpoint_custom(line, custom, check=True):
    h.line_endpoint_custom.associate(line['id'], custom['id'], check)
    yield
    h.line_endpoint_custom.dissociate(line['id'], custom['id'], check)


@contextmanager
def user_call_permission(user, call_permission, check=True):
    h.user_call_permission.associate(user['id'], call_permission['id'], check)
    yield
    h.user_call_permission.dissociate(user['id'], call_permission['id'], check)


@contextmanager
def user_entity(user, entity, check=True):
    h.user_entity.associate(user['id'], entity['id'], check)
    yield


@contextmanager
def user_agent(user, agent, check=True):
    h.user_agent.associate(user['id'], agent['id'], check)
    yield
    h.user_agent.dissociate(user['id'], agent['id'], check)


@contextmanager
def user_funckey_template(user, funckey_template, check=True):
    h.user_funckey_template.associate(user['id'], funckey_template['id'], check)
    yield
    h.user_funckey_template.dissociate(user['id'], funckey_template['id'], check)


@contextmanager
def call_filter_entity(call_filter, entity, check=True):
    h.call_filter_entity.associate(call_filter['id'], entity['id'], check)
    yield


@contextmanager
def call_pickup_entity(call_pickup, entity, check=True):
    h.call_pickup_entity.associate(call_pickup['id'], entity['id'], check)
    yield


@contextmanager
def context_entity(context, entity, check=True):
    h.context_entity.associate(context['name'], entity['name'], check)
    yield


@contextmanager
def schedule_entity(schedule, entity, check=True):
    h.schedule_entity.associate(schedule['id'], entity['id'], check)
    yield


@contextmanager
def queue_extension(queue, extension, check=True):
    h.queue_extension.associate(queue['id'], extension['id'], check)
    yield
    h.queue_extension.dissociate(queue['id'], extension['id'], check)


@contextmanager
def trunk_endpoint_sip(trunk, sip, check=True):
    h.trunk_endpoint_sip.associate(trunk['id'], sip['id'], check)
    yield
    h.trunk_endpoint_sip.dissociate(trunk['id'], sip['id'], check)


@contextmanager
def trunk_endpoint_custom(trunk, custom, check=True):
    h.trunk_endpoint_custom.associate(trunk['id'], custom['id'], check)
    yield
    h.trunk_endpoint_custom.dissociate(trunk['id'], custom['id'], check)


@contextmanager
def incall_extension(incall, extension, check=True):
    h.incall_extension.associate(incall['id'], extension['id'], check)
    yield
    h.incall_extension.dissociate(incall['id'], extension['id'], check)


@contextmanager
def incall_user(incall, user, check=True):
    h.incall_user.associate(incall['id'], user['id'], check)
    yield
    h.incall_user.dissociate(incall['id'], user['id'], check)


@contextmanager
def outcall_trunk(outcall, *trunks, **kwargs):
    trunk_ids = [trunk['id'] for trunk in trunks]
    check = kwargs.get('check', True)
    h.outcall_trunk.associate(outcall['id'], trunk_ids, check=check)
    yield
    h.outcall_trunk.dissociate(outcall['id'], check=check)


@contextmanager
def outcall_extension(outcall, extension, **kwargs):
    h.outcall_extension.associate(outcall['id'], extension['id'], **kwargs)
    yield
    h.outcall_extension.dissociate(outcall['id'], extension['id'], **kwargs)


@contextmanager
def queue_member_agent(queue, agent, **kwargs):
    h.queue_member_agent.associate(queue['id'], agent['id'], **kwargs)
    yield
    h.queue_member_agent.dissociate(queue['id'], agent['id'], **kwargs)


@contextmanager
def group_extension(group, extension, check=True):
    h.group_extension.associate(group['id'], extension['id'], check)
    yield
    h.group_extension.dissociate(group['id'], extension['id'], check)


@contextmanager
def group_member_user(group, *users, **kwargs):
    user_uuids = [user['uuid'] for user in users]
    check = kwargs.get('check', True)
    h.group_member_user.associate(group['id'], user_uuids, check=check)
    yield
    h.group_member_user.dissociate(group['id'], check=check)


@contextmanager
def conference_extension(conference, extension, check=True):
    h.conference_extension.associate(conference['id'], extension['id'], check)
    yield
    h.conference_extension.dissociate(conference['id'], extension['id'], check)


@contextmanager
def parking_lot_extension(parking_lot, extension, check=True):
    h.parking_lot_extension.associate(parking_lot['id'], extension['id'], check)
    yield
    h.parking_lot_extension.dissociate(parking_lot['id'], extension['id'], check)


@contextmanager
def paging_member_user(paging, *users, **kwargs):
    user_uuids = [user['uuid'] for user in users]
    check = kwargs.get('check', True)
    h.paging_member_user.associate(paging['id'], user_uuids, check=check)
    yield
    h.paging_member_user.dissociate(paging['id'], check=check)


@contextmanager
def paging_caller_user(paging, *users, **kwargs):
    user_uuids = [user['uuid'] for user in users]
    check = kwargs.get('check', True)
    h.paging_caller_user.associate(paging['id'], user_uuids, check=check)
    yield
    h.paging_caller_user.dissociate(paging['id'], check=check)


@contextmanager
def switchboard_member_user(switchboard, users, check=True):
    user_uuids = [user['uuid'] for user in users]
    h.switchboard_member_user.associate(switchboard['uuid'], user_uuids, check=check)
    yield
    h.switchboard_member_user.dissociate(switchboard['uuid'], check=check)


@contextmanager
def incall_schedule(incall, schedule, check=True):
    h.incall_schedule.associate(incall['id'], schedule['id'], check)
    yield
    h.incall_schedule.dissociate(incall['id'], schedule['id'], check)
