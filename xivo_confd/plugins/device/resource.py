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

from flask import url_for

from .schema import DeviceSchema
from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource, ConfdResource
from xivo_confd.plugins.device.model import Device


class DeviceList(ListResource):

    model = Device.from_args
    schema = DeviceSchema

    def build_headers(self, device):
        return {'Location': url_for('devices', id=device.id, _external=True)}

    @required_acl('confd.devices.read')
    def get(self):
        return super(DeviceList, self).get()

    @required_acl('confd.devices.create')
    def post(self):
        return super(DeviceList, self).post()


class DeviceItem(ItemResource):

    schema = DeviceSchema

    @required_acl('confd.devices.{id}.read')
    def get(self, id):
        return super(DeviceItem, self).get(id)

    @required_acl('confd.devices.{id}.update')
    def put(self, id):
        return super(DeviceItem, self).put(id)

    @required_acl('confd.devices.{id}.delete')
    def delete(self, id):
        return super(DeviceItem, self).delete(id)


class DeviceAutoprov(ConfdResource):

    def __init__(self, service):
        self.service = service

    @required_acl('confd.devices.{id}.autoprov.read')
    def get(self, id):
        device = self.service.get(id)
        self.service.reset_autoprov(device)
        return ('', 204)


class DeviceSynchronize(ConfdResource):

    def __init__(self, service):
        self.service = service

    @required_acl('confd.devices.{id}.synchronize.read')
    def get(self, id):
        device = self.service.get(id)
        self.service.synchronize(device)
        return ('', 204)
