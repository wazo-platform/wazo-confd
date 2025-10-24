# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields, post_load, pre_dump
from marshmallow.validate import Length
from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.mallow import BaseSchema, Nested
from wazo_confd.helpers.restful import ConfdResource


class IAXCallNumberLimitsSchema(BaseSchema):
    ip_address = fields.String(
        required=True, validate=(Length(max=39)), attribute='destination'
    )
    netmask = fields.String(required=True, validate=(Length(max=39)))
    limit = fields.Integer(required=True, attribute='calllimits')


class IAXCallNumberLimitsCollectionSchema(BaseSchema):
    items = Nested(IAXCallNumberLimitsSchema, many=True, required=True)

    @post_load
    def remove_envelope(self, data, **kwargs):
        return data['items']

    @pre_dump
    def add_envelope(self, data, **kwargs):
        return {'items': [option for option in data]}


class IAXCallNumberLimitsList(ConfdResource):
    model = IAXCallNumberLimits
    schema = IAXCallNumberLimitsCollectionSchema

    def __init__(self, service):
        super().__init__()
        self.service = service

    @required_master_tenant()
    @required_acl('confd.asterisk.iax.callnumberlimits.get')
    def get(self):
        options = self.service.list()
        return self.schema().dump(options)

    @required_master_tenant()
    @required_acl('confd.asterisk.iax.callnumberlimits.update')
    def put(self):
        form = self.schema().load(request.get_json(force=True))
        iax_callnumberlimits = [self.model(**option) for option in form]
        self.service.edit(iax_callnumberlimits)
        return '', 204
