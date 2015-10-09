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

from collections import namedtuple

from xivo_dao.helpers import errors

from xivo_confd.plugins.line.service import build_service as build_line_service
from xivo_confd.plugins.endpoint_sip.service import build_service as build_sip_service

LineEndpointSip = namedtuple('LineEndpointSip', ['line_id', 'sip_id'])


class LineEndpointService(object):

    def __init__(self, line_service, sip_service):
        self.line_service = line_service
        self.sip_service = sip_service

    def get_line(self, line_id):
        return self.line_service.get(line_id)

    def get_sip(self, sip_id):
        return self.sip_service.get(sip_id)

    def get_association_from_line(self, line_id):
        line = self.line_service.find_by(id=line_id)

        if not line:
            raise errors.not_found('Line', id=line_id)
        if line.endpoint != 'sip' or line.endpoint_id is None:
            raise errors.not_found('LineEndpoint', line_id=line_id)

        return {'line_id': line.id,
                'sip_id': line.endpoint_id}

    def get_association_from_endpoint(self, sip_id):
        sip = self.sip_service.get(sip_id)
        if not sip:
            raise errors.not_found('SIPEndpoint', id=sip_id)

        line = self.line_service.find_by(protocol='sip', protocolid=sip_id)
        if not line:
            raise errors.not_found('LineEndpoint', sip_id=sip_id)

        return {'line_id': line.id,
                'sip_id': line.endpoint_id}

    def associate(self, line, sip):
        if line.endpoint is not None and line.endpoint_id is not None:
            raise errors.resource_associated('Line', 'Endpoint',
                                             line_id=line.id,
                                             endpoint=line.endpoint,
                                             endpoint_id=line.endpoint_id)

        line.endpoint = 'sip'
        line.endpoint_id = sip.id
        self.line_service.edit(line)

    def dissociate(self, line, sip):
        if line.endpoint != 'sip' and line.endpoint_id != sip.id:
            raise errors.resource_not_associated('Line', 'Endpoint',
                                                 line_id=line.id,
                                                 endpoint='sip',
                                                 endpoint_id=sip.id)
        line.endpoint = None
        line.endpoint_id = None
        self.line_service.edit(line)


def build_service():
    line_service = build_line_service()
    sip_service = build_sip_service()
    return LineEndpointService(line_service, sip_service)
