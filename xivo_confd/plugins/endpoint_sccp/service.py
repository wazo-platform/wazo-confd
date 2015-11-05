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

from xivo_dao.resources.endpoint_sccp import dao

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.plugins.endpoint_sccp.validator import build_validator
from xivo_confd.plugins.endpoint_sccp.notifier import build_notifier


class SccpEndpointService(CRUDService):
    pass


def build_service():
    return SccpEndpointService(dao,
                               build_validator(),
                               build_notifier())
