# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class TrunkRegisterAssociation(ConfdResource):

    def __init__(self, service, trunk_dao, register_dao):
        super(TrunkRegisterAssociation, self).__init__()
        self.service = service
        self.trunk_dao = trunk_dao
        self.register_dao = register_dao

    def put(self, trunk_id, register_id):
        trunk = self.trunk_dao.get(trunk_id)
        register = self.register_dao.get(register_id)
        self.service.associate(trunk, register)
        return '', 204

    def delete(self, trunk_id, register_id):
        trunk = self.trunk_dao.get(trunk_id)
        register = self.register_dao.get(register_id)
        self.service.dissociate(trunk, register)
        return '', 204


class TrunkRegisterAssociationIAX(TrunkRegisterAssociation):

    @required_acl('confd.trunks.{trunk_id}.registers.iax.{register_id}.update')
    def put(self, trunk_id, register_id):
        return super(TrunkRegisterAssociationIAX, self).put(trunk_id, register_id)

    @required_acl('confd.trunks.{trunk_id}.registers.iax.{register_id}.delete')
    def delete(self, trunk_id, register_id):
        return super(TrunkRegisterAssociationIAX, self).delete(trunk_id, register_id)


class TrunkRegisterAssociationSIP(TrunkRegisterAssociation):

    @required_acl('confd.trunks.{trunk_id}.registers.sip.{register_id}.update')
    def put(self, trunk_id, register_id):
        return super(TrunkRegisterAssociationSIP, self).put(trunk_id, register_id)

    @required_acl('confd.trunks.{trunk_id}.registers.sip.{register_id}.delete')
    def delete(self, trunk_id, register_id):
        return super(TrunkRegisterAssociationSIP, self).delete(trunk_id, register_id)
