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

from xivo_confd.helpers.associations import ValidateLineAssociation, VaildateLineDissociation
from xivo_confd.plugins.line.service import build_service as build_line_service
from xivo_confd.plugins.endpoint_sip.service import build_service as build_sip_service
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao


class LineEndpointSipService(object):

    def __init__(self, line_service, sip_service, association_validator, dissociation_validator):
        self.line_service = line_service
        self.sip_service = sip_service
        self.association_validator = association_validator
        self.dissociation_validator = dissociation_validator

    def get_line(self, line_id):
        return self.line_service.get(line_id)

    def get_sip(self, sip_id):
        return self.sip_service.get(sip_id)

    def get_association_from_line(self, line_id):
        line = self.line_service.find_by(id=line_id)

        if not line:
            raise errors.not_found('Line', id=line_id)
        if line.endpoint != 'sip' or line.endpoint_id is None:
            raise errors.not_found('LineEndpointSip', line_id=line_id)

        return {'line_id': line.id,
                'sip_id': line.endpoint_id}

    def get_association_from_endpoint(self, sip_id):
        sip = self.sip_service.get(sip_id)
        if not sip:
            raise errors.not_found('SIPEndpoint', id=sip_id)

        line = self.line_service.find_by(protocol='sip', protocolid=sip_id)
        if not line:
            raise errors.not_found('LineEndpointSip', sip_id=sip_id)

        return {'line_id': line.id,
                'sip_id': line.endpoint_id}

    def associate(self, line, sip):
        self.association_validator.validate(line)
        line.endpoint = 'sip'
        line.endpoint_id = sip.id
        self.line_service.edit(line)

    def dissociate(self, line, sip):
        self.dissociation_validator.validate(line, sip)
        line.endpoint = None
        line.endpoint_id = None
        self.line_service.edit(line)


def build_service(provd_client):
    association_validator = ValidateLineAssociation()
    dissociation_validator = VaildateLineDissociation(user_line_dao, line_extension_dao)
    line_service = build_line_service(provd_client)
    sip_service = build_sip_service(provd_client)
    return LineEndpointSipService(line_service, sip_service, association_validator, dissociation_validator)
