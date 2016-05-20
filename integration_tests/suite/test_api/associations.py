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
def user_funckey_template(user, funckey_template, check=True):
    h.user_funckey_template.associate(user['id'], funckey_template['id'], check)
    yield
    h.user_funckey_template.dissociate(user['id'], funckey_template['id'], check)
