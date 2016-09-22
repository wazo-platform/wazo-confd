# -*- coding: UTF-8 -*-

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

from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ConfdResource


class IncallExtensionSchema(BaseSchema):
    incall_id = fields.Integer(attribute='typeval')
    extension_id = fields.Integer(attribute='id')
    links = ListLink(Link('incalls',
                          field='typeval',
                          target='id'),
                     Link('extensions',
                          field='id',
                          target='id'))


class IncallExtensionResource(ConfdResource):

    def __init__(self, service, incall_dao, extension_dao):
        super(ConfdResource, self).__init__()
        self.service = service
        self.incall_dao = incall_dao
        self.extension_dao = extension_dao


class ExtensionIncallList(IncallExtensionResource):

    schema = IncallExtensionSchema

    @required_acl('confd.extensions.{extension_id}.incalls.read')
    def get(self, extension_id):
        extension = self.extension_dao.get(extension_id)
        items = self.service.find_all_by_extension_id(extension.id)
        return {'total': len(items),
                'items': self.schema().dump(items, many=True).data}


class IncallExtensionList(IncallExtensionResource):

    schema = IncallExtensionSchema

    @required_acl('confd.incalls.{incall_id}.extensions.read')
    def get(self, incall_id):
        incall = self.incall_dao.get(incall_id)
        items = self.service.find_all_by_incall_id(incall.id)
        return {'total': len(items),
                'items': self.schema().dump(items, many=True).data}


class IncallExtensionItem(IncallExtensionResource):

    @required_acl('confd.incalls.{incall_id}.extensions.{extension_id}.delete')
    def delete(self, incall_id, extension_id):
        incall = self.incall_dao.get(incall_id)
        extension = self.extension_dao.get(extension_id)
        self.service.dissociate(incall, extension)
        return '', 204

    @required_acl('confd.incalls.{incall_id}.extensions.{extension_id}.update')
    def put(self, incall_id, extension_id):
        incall = self.incall_dao.get(incall_id)
        extension = self.extension_dao.get(extension_id)
        self.service.associate(incall, extension)
        return '', 204
