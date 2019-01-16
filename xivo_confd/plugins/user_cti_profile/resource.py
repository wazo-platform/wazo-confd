# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from flask import request
from marshmallow import fields

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean
from xivo_confd.helpers.restful import ConfdResource


class UserCtiProfileSchema(BaseSchema):
    user_id = fields.Integer(dump_only=True, attribute='id')
    enabled = StrictBoolean(attribute='cti_enabled')
    cti_profile_id = fields.Integer(allow_none=True, attribute='cti_profile_id')
    links = ListLink(Link('cti_profiles',
                          field='cti_profile_id',
                          target='id'),
                     Link('users',
                          field='id',
                          target='id'))


class UserCtiProfileRoot(ConfdResource):

    schema = UserCtiProfileSchema

    def __init__(self, service, user_dao, cti_profile_dao):
        super(UserCtiProfileRoot, self).__init__()
        self.service = service
        self.user_dao = user_dao
        self.cti_profile_dao = cti_profile_dao

    @required_acl('confd.users.{user_id}.cti.read')
    def get(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        return self.schema().dump(user).data

    @required_acl('confd.users.{user_id}.cti.update')
    def put(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        form = self.schema().load(request.get_json()).data
        self.service.edit(user, form)
        return '', 204
