# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from marshmallow import fields, pre_dump, post_load
from marshmallow.validate import Length

from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource


class IAXCallNumberLimitsSchema(BaseSchema):
    ip_address = fields.String(required=True, validate=(Length(max=39)), attribute='destination')
    netmask = fields.String(required=True, validate=(Length(max=39)))
    limit = fields.Integer(required=True, attribute='calllimits')


class IAXCallNumberLimitsCollectionSchema(BaseSchema):
    items = fields.Nested(IAXCallNumberLimitsSchema,
                          many=True,
                          required=True)

    @post_load
    def remove_envelope(self, data):
        return data['items']

    @pre_dump
    def add_envelope(self, data):
        return {'items': [option for option in data]}


class IAXCallNumberLimitsList(ConfdResource):

    model = IAXCallNumberLimits
    schema = IAXCallNumberLimitsCollectionSchema

    def __init__(self, service):
        super(IAXCallNumberLimitsList, self).__init__()
        self.service = service

    @required_acl('confd.asterisk.iax.callnumberlimits.get')
    def get(self):
        options = self.service.list()
        return self.schema().dump(options).data

    @required_acl('confd.asterisk.iax.callnumberlimits.update')
    def put(self):
        form = self.schema().load(request.get_json()).data
        iax_callnumberlimits = [self.model(**option) for option in form]
        self.service.edit(iax_callnumberlimits)
        return '', 204
