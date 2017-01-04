# -*- coding: UTF-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
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


from flask import request
from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean
from xivo_confd.helpers.restful import ConfdResource


class UserCtiProfileSchema(BaseSchema):
    user_id = fields.Integer(dump_only=True, attribute='id')
    enabled = StrictBoolean(attribute='cti_enabled')
    cti_profile_id = fields.Integer(missing=None, attribute='cti_profile_id')
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
