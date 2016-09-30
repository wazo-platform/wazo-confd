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

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource
from xivo_confd.plugins.endpoint_sip.schema import SipSchema
from xivo_confd.database import user_line_associated as user_line_associated_db


class UserLineAssociatedEndpointSipMain(ConfdResource):

    schema = SipSchema

    @required_acl('confd.users.{user_uuid}.lines.main.associated.endpoints.sip.read')
    def get(self, user_uuid):
        endpoint_sip = user_line_associated_db.find_main_endpoint_sip_by_user(user_uuid)
        if endpoint_sip is None:
            return 'Resource Not Found.', 404

        return self.schema().dump(endpoint_sip).data
