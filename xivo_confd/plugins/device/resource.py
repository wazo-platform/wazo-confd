# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource, ConfdResource
from xivo_confd.plugins.device.model import Device

from .schema import DeviceSchema


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
