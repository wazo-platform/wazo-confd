# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

from flask import request
from flask import Response
from flask import url_for

from xivo_dao.alchemy.moh import MOH

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource, ItemResource, ListResource

from .schema import MohSchema, MohSchemaPUT


class MohList(ListResource):

    model = MOH
    schema = MohSchema

    def build_headers(self, moh):
        return {'Location': url_for('moh', uuid=moh.uuid, _external=True)}

    @required_acl('confd.moh.create')
    def post(self):
        return super(MohList, self).post()

    @required_acl('confd.moh.read')
    def get(self):
        return super(MohList, self).get()


class MohItem(ItemResource):

    schema = MohSchemaPUT

    @required_acl('confd.moh.{uuid}.read')
    def get(self, uuid):
        return super(MohItem, self).get(uuid)

    @required_acl('confd.moh.{uuid}.update')
    def put(self, uuid):
        return super(MohItem, self).put(uuid)

    @required_acl('confd.moh.{uuid}.delete')
    def delete(self, uuid):
        return super(MohItem, self).delete(uuid)


class MohFileItem(ConfdResource):

    def __init__(self, service):
        self.service = service

    @required_acl('confd.moh.{uuid}.files.{filename}.read')
    def get(self, uuid, filename):
        moh = self.service.get(uuid)
        response = self.service.load_file(moh, filename)
        return response

    @required_acl('confd.moh.{uuid}.files.{filename}.update')
    def put(self, uuid, filename):
        moh = self.service.get(uuid)
        self.service.save_file(moh, filename, request.data)
        return '', 204

    @required_acl('confd.moh.{uuid}.files.{filename}.delete')
    def delete(self, uuid, filename):
        moh = self.service.get(uuid)
        self.service.delete_file(moh, filename)
        return '', 204
