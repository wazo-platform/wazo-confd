# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

from flask import url_for

from xivo_dao.alchemy.switchboard import Switchboard

from .schema import SwitchboardSchema
from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource


class SwitchboardList(ListResource):

    model = Switchboard
    schema = SwitchboardSchema

    def build_headers(self, switchboard):
        return {'Location': url_for('switchboards', uuid=switchboard.uuid, _external=True)}

    @required_acl('confd.switchboards.create')
    def post(self):
        return super(SwitchboardList, self).post()

    @required_acl('confd.switchboards.read')
    def get(self):
        return super(SwitchboardList, self).get()


class SwitchboardItem(ItemResource):

    schema = SwitchboardSchema

    @required_acl('confd.switchboards.{uuid}.read')
    def get(self, uuid):
        return super(SwitchboardItem, self).get(uuid)

    @required_acl('confd.switchboards.{uuid}.update')
    def put(self, uuid):
        return super(SwitchboardItem, self).put(uuid)

    @required_acl('confd.switchboards.{uuid}.delete')
    def delete(self, uuid):
        return super(SwitchboardItem, self).delete(uuid)
