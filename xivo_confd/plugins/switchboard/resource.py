# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


from flask_restful import fields, marshal

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource
from xivo_confd.helpers.restful import ListResource

from xivo_confd.plugins.switchboard.model import Switchboard

switchboard_fields = {
    'id': fields.String,
}


class SwitchboardList(ListResource):

    model = Switchboard
    fields = switchboard_fields

    def __init__(self, service):
        self.service = service

    @required_acl('confd.switchboards.read')
    def get(self):
        params = self.search_params()
        result = self.service.search(params)
        return {'total': result.total,
                'items': [marshal(item, switchboard_fields) for item in result.items]}
