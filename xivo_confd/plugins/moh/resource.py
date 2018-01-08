# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request, url_for

from xivo_dao.alchemy.moh import MOH

from xivo_confd.auth import required_acl
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
