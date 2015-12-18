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

from test_api.helpers import user_line as ul
from test_api.helpers import user_cti_profile as uc
from test_api.helpers import user_voicemail as uv
from test_api.helpers import line_extension as le
from test_api.helpers import line_device as ld
from test_api.helpers import line_endpoint_sip as l_endpoint_sip
from test_api.helpers import line_endpoint_sccp as l_endpoint_sccp


@contextmanager
def user_line(user, line, check=True):
    ul.associate(user['id'], line['id'], check)
    yield
    ul.dissociate(user['id'], line['id'], check)


@contextmanager
def user_voicemail(user, voicemail, check=True):
    uv.associate(user['id'], voicemail['id'], check)
    yield
    uv.dissociate(user['id'], voicemail['id'], check)


@contextmanager
def user_cti_profile(user, cti_profile, check=True):
    uc.associate(user['id'], cti_profile['id'])
    yield
    uc.dissociate(user['id'], cti_profile['id'])


@contextmanager
def line_extension(line, extension, check=True):
    le.associate(line['id'], extension['id'], check)
    yield
    le.dissociate(line['id'], extension['id'], check)


@contextmanager
def line_device(line, device, check=True):
    ld.associate(line['id'], device['id'])
    yield
    try:
        ld.dissociate(line['id'], device['id'])
    except Exception as e:
        if check:
            raise e


@contextmanager
def line_endpoint_sip(line, sip, check=True):
    l_endpoint_sip.associate(line['id'], sip['id'], check)
    yield
    l_endpoint_sip.dissociate(line['id'], sip['id'], check)


@contextmanager
def line_endpoint_sccp(line, sccp, check=True):
    l_endpoint_sccp.associate(line['id'], sccp['id'], check)
    yield
    l_endpoint_sccp.dissociate(line['id'], sccp['id'], check)
