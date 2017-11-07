# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from marshmallow import fields, post_dump, pre_load, pre_dump, post_load
from marshmallow.validate import Length, NoneOf

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource

from xivo_dao.alchemy.staticsip import StaticSIP

REGISTER_ERROR = "The 'register' key can only be defined in trunk options"


class SIPGeneralOption(BaseSchema):
    key = fields.String(validate=(Length(max=128),
                                  NoneOf(['register'], error=REGISTER_ERROR)),
                        required=True,
                        attribute='var_name')
    value = fields.String(validate=Length(max=255),
                          required=True,
                          attribute='var_val')


class SIPGeneralOrderedOption(SIPGeneralOption):
    @pre_load
    def add_envelope(self, data):
        if isinstance(data, list) and len(data) == 2:
            return {'key': data[0], 'value': data[1]}

    @post_dump
    def remove_envelope(self, data):
        return [data['key'], data['value']]


class SIPGeneralSchema(BaseSchema):
    options = fields.Nested(SIPGeneralOption,
                            many=True,
                            required=True)

    ordered_options = fields.List(fields.Nested(SIPGeneralOrderedOption),
                                  required=True)

    @pre_load
    def convert_options_to_collection(self, data):
        options = data.get('options')
        if isinstance(options, dict):
            data['options'] = [{'key': key, 'value': value} for key, value in options.iteritems()]
        return data

    @post_load
    def merge_options_and_ordered_options(self, data):
        self._add_metric(data)
        result = []
        result.extend(data['options'])
        result.extend(data['ordered_options'])
        return result

    def _add_metric(self, data):
        for metric, ordered_option in enumerate(data['ordered_options']):
            ordered_option['metric'] = metric
        for option in data['options']:
            option['metric'] = None

    @pre_dump
    def separate_options_and_ordered_options(self, data):
        return {'options': [option for option in data if option.metric is None],
                'ordered_options': [option for option in data if option.metric is not None]}

    @post_dump
    def convert_options_to_dict(self, data):
        data['options'] = {option['key']: option['value'] for option in data['options']}
        return data


class SIPGeneralList(ConfdResource):

    model = StaticSIP
    schema = SIPGeneralSchema

    def __init__(self, service):
        super(SIPGeneralList, self).__init__()
        self.service = service

    @required_acl('confd.asterisk.sip.general.get')
    def get(self):
        options = self.service.list()
        return self.schema().dump(options).data

    @required_acl('confd.asterisk.sip.general.update')
    def put(self):
        form = self.schema().load(request.get_json()).data
        sip_general = [StaticSIP(**option) for option in form]
        self.service.edit(sip_general)
        return '', 204
