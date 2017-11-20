# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
