# -*- coding: UTF-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ConfdResource


class UserEntitySchema(BaseSchema):
    user_id = fields.Integer()
    entity_id = fields.Integer()
    links = ListLink(Link('users',
                          field='user_id',
                          target='id'),
                     Link('entities',
                          field='entity_id',
                          target='id'))


class UserEntityResource(ConfdResource):

    def __init__(self, service, user_dao, entity_dao):
        super(UserEntityResource, self).__init__()
        self.service = service
        self.user_dao = user_dao
        self.entity_dao = entity_dao


class UserEntityItem(UserEntityResource):

    @required_acl('confd.users.{user_id}.entities.{entity_id}.update')
    def put(self, user_id, entity_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        entity = self.entity_dao.get(entity_id)
        self.service.associate(user, entity)
        return '', 204


class UserEntityList(UserEntityResource):

    schema = UserEntitySchema

    @required_acl('confd.users.{user_id}.entities.read')
    def get(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        item = self.service.find_by(user_id=user.id)
        return self.schema().dump(item).data
