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

from xivo_dao.helpers import errors

from xivo_confd.plugins.line_sip.model import LineSip

from xivo_confd.plugins.line.service import build_service as build_line_service
from xivo_confd.plugins.endpoint_sip.service import build_service as build_sip_service


class LineSipService(object):

    def __init__(self, line_service, sip_service):
        self.line_service = line_service
        self.sip_service = sip_service

    def get(self, id):
        line = self.line_service.get(id)
        if line.sip_endpoint is None:
            raise errors.not_found('LineSIP', id=id)
        return LineSip.from_line_and_sip(line, line.sip_endpoint)

    def search(self, params):
        total, items = self.line_service.search(params)
        items = (LineSip.from_line_and_sip(line, line.sip_endpoint)
                 for line in items
                 if line.sip_endpoint is not None)
        return total, items

    def create(self, line_sip):
        sip = self.create_sip(line_sip)
        try:
            line = self.create_line(line_sip, sip)
        except Exception:
            self.sip_service.delete(sip)
            raise
        return LineSip.from_line_and_sip(line, sip)

    def create_sip(self, line_sip):
        sip = line_sip.build_sip()
        created_sip = self.sip_service.create(sip)
        return created_sip

    def create_line(self, line_sip, sip):
        line = line_sip.build_line(sip)
        return self.line_service.create(line)

    def edit(self, line_sip):
        line = self.line_service.get(line_sip.id)
        sip = self.sip_service.get(line.protocolid)

        line_sip.update_sip(sip)
        line_sip.update_line(line)

        self.sip_service.edit(sip)
        self.line_service.edit(line)

    def delete(self, line_sip):
        line = self.line_service.get(line_sip.id)
        sip = self.sip_service.get(line.protocolid)
        self.line_service.delete(line)
        self.sip_service.delete(sip)


def build_service(provd_client):
    return LineSipService(build_line_service(provd_client),
                          build_sip_service(provd_client))
