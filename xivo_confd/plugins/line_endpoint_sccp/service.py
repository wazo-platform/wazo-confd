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
from xivo_confd.plugins.endpoint_sccp.service import build_service as build_sccp_service
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao


class LineEndpointSccpService(object):

    def __init__(self, line_service, sccp_service, association_validator, dissociation_validator):
        self.line_service = line_service
        self.sccp_service = sccp_service
        self.association_validator = association_validator
        self.dissociation_validator = dissociation_validator

    def get_line(self, line_id):
        return self.line_service.get(line_id)

    def get_sccp(self, sccp_id):
        return self.sccp_service.get(sccp_id)

    def get_association_from_line(self, line_id):
        line = self.line_service.get(line_id)
        if not line.is_associated('sccp'):
            raise errors.not_found('LineEndpointSccp', line_id=line_id)

        return {'line_id': line.id,
                'sccp_id': line.endpoint_id}

    def get_association_from_endpoint(self, sccp_id):
        sccp = self.sccp_service.get(sccp_id)
        line = self.line_service.find_by(protocol='sccp', protocolid=sccp.id)
        if not line:
            raise errors.not_found('LineEndpointSccp', sccp_id=sccp_id)

        return {'line_id': line.id,
                'sccp_id': line.endpoint_id}

    def associate(self, line, sccp):
        self.association_validator.validate(line)
        line.endpoint = 'sccp'
        line.endpoint_id = sccp.id
        self.line_service.edit(line)

    def dissociate(self, line, sccp):
        self.dissociation_validator.validate(line, sccp)
        line.endpoint = None
        line.endpoint_id = None
        self.line_service.edit(line)


def build_service(provd_client):
    association_validator = ValidateLineAssociation()
    dissociation_validator = VaildateLineDissociation(user_line_dao, line_extension_dao)
    line_service = build_line_service(provd_client)
    sccp_service = build_sccp_service()
    return LineEndpointSccpService(line_service, sccp_service, association_validator, dissociation_validator)
