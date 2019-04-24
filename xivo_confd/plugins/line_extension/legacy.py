# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers import errors

from flask import url_for, request
from marshmallow import fields

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class LineExtensionLegacySchema(BaseSchema):
    line_id = fields.Integer(dump_only=True)
    extension_id = fields.Integer(required=True)
    links = ListLink(Link('lines',
                          field='line_id',
                          target='id'),
                     Link('extensions',
                          field='extension_id',
                          target='id'))


class LegacyResource(ConfdResource):

    schema = LineExtensionLegacySchema

    def __init__(self, service, line_dao, extension_dao, line_extension_dao):
        super(LegacyResource, self).__init__()
        self.service = service
        self.line_dao = line_dao
        self.extension_dao = extension_dao
        self.line_extension_dao = line_extension_dao

    def get_extension_or_fail(self):
        form = self.schema().load(request.get_json()).data
        try:
            return self.extension_dao.get(form['extension_id'])
        except NotFoundError:
            raise errors.param_not_found('extension_id', 'Extension')


class LineExtensionLegacy(LegacyResource):

    @required_acl('confd.#')
    def get(self, line_id):
        line = self.line_dao.get(line_id)
        line_extension = self.line_extension_dao.get_by(line_id=line.id)
        return self.schema().dump(line_extension).data

    @required_acl('confd.#')
    def post(self, line_id):
        line = self.line_dao.get(line_id)
        extension = self.get_extension_or_fail()
        line_extension = self.service.associate(line, extension)
        return self.schema().dump(line_extension).data, 201, self.build_headers(line_extension)

    @required_acl('confd.#')
    def delete(self, line_id):
        line = self.line_dao.get(line_id)
        line_extension = self.line_extension_dao.get_by(line_id=line.id)
        extension = self.extension_dao.get(line_extension.extension_id)
        self.service.dissociate(line, extension)
        return '', 204

    def build_headers(self, model):
        url = url_for('line_extension_legacy',
                      line_id=model.line_id,
                      _external=True)
        return {'Location': url}


class ExtensionLineLegacy(LegacyResource):

    @required_acl('confd.#')
    def get(self, extension_id):
        extension = self.extension_dao.get(extension_id)
        line_extension = self.line_extension_dao.get_by(extension_id=extension.id)
        return self.schema().dump(line_extension).data
