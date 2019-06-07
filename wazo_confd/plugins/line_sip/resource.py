# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for
from marshmallow import fields
from marshmallow.validate import Length, Predicate, Range, Regexp

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ListResource, ItemResource
from xivo_confd.plugins.line_sip.model import LineSip


USERNAME_REGEX = r'^[a-zA-Z0-9]+$'
SECRET_REGEX = r'^[a-zA-Z0-9]+$'
CALLERID_REGEX = r'"[^"]+"(\s+<[+0-9]>)?'


class LineSipSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    username = fields.String(validate=Regexp(USERNAME_REGEX))
    secret = fields.String(validate=Regexp(SECRET_REGEX))
    callerid = fields.String(validate=Regexp(CALLERID_REGEX), allow_none=True)
    device_slot = fields.Integer(validate=Range(min=0))
    context = fields.String(required=True)
    provisioning_extension = fields.String(validate=(Length(equal=6), Predicate('isdigit')))
    links = ListLink(Link('lines'),
                     Link('lines_sip'))


class LineSipList(ListResource):

    model = LineSip
    schema = LineSipSchema

    @required_acl('confd.#')
    def get(self):
        params = self.search_params()
        total, items = self.service.search(params)
        return {'total': total,
                'items': self.schema().dump(items, many=True).data}

    @required_acl('confd.#')
    def post(self):
        return super(LineSipList, self).post()

    def build_headers(self, line):
        return {'Location': url_for('lines_sip', id=line.id, _external=True)}

    def _has_write_tenant_uuid(self):
        return True


class LineSipItem(ItemResource):

    schema = LineSipSchema

    @required_acl('confd.#')
    def get(self, id):
        return super(LineSipItem, self).get(id)

    @required_acl('confd.#')
    def put(self, id):
        return super(LineSipItem, self).put(id)

    @required_acl('confd.#')
    def delete(self, id):
        return super(LineSipItem, self).delete(id)
