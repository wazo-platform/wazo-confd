# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from marshmallow import fields, pre_dump, post_load, pre_load, post_dump
from marshmallow.validate import Length

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource

from xivo_dao.alchemy.asterisk_file_variable import AsteriskFileVariable


class AsteriskOptionSchema(BaseSchema):
    key = fields.String(validate=Length(max=255), required=True)
    value = fields.String(required=True)


class ConfBridgeConfigurationSchema(BaseSchema):
    options = fields.Nested(AsteriskOptionSchema, many=True, required=True)

    @pre_load
    def convert_options_to_collection(self, data):
        options = data.get('options')
        if isinstance(options, dict):
            data['options'] = [{'key': key, 'value': value} for key, value in options.iteritems()]
        return data

    @post_dump
    def convert_options_to_dict(self, data):
        data['options'] = {option['key']: option['value'] for option in data['options']}
        return data

    @pre_dump
    def add_envelope(self, data):
        return {'options': data}

    @post_load
    def remove_envelope(self, data):
        return data['options']


class ConfBridgeConfigurationList(ConfdResource):
    model = AsteriskFileVariable
    schema = ConfBridgeConfigurationSchema
    section_name = None

    def __init__(self, service):
        super(ConfBridgeConfigurationList, self).__init__()
        self.service = service

    def get(self):
        options = self.service.list(section=self.section_name)
        return self.schema().dump(options).data

    def put(self):
        form = self.schema().load(request.get_json()).data
        variables = [self.model(**option) for option in form]
        self.service.edit(self.section_name, variables)
        return '', 204


class ConfBridgeDefaultBridgeList(ConfBridgeConfigurationList):
    section_name = 'default_bridge'

    @required_acl('confd.asterisk.confbridge.default_bridge.get')
    def get(self):
        return super(ConfBridgeDefaultBridgeList, self).get()

    @required_acl('confd.asterisk.confbridge.default_bridge.update')
    def put(self):
        return super(ConfBridgeDefaultBridgeList, self).put()


class ConfBridgeDefaultUserList(ConfBridgeConfigurationList):
    section_name = 'default_user'

    @required_acl('confd.asterisk.confbridge.default_user.get')
    def get(self):
        return super(ConfBridgeDefaultUserList, self).get()

    @required_acl('confd.asterisk.confbridge.default_user.update')
    def put(self):
        return super(ConfBridgeDefaultUserList, self).put()
