# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields, post_dump, post_load, pre_dump, pre_load
from marshmallow.validate import Length, NoneOf
from xivo_dao.alchemy.staticiax import StaticIAX

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.mallow import BaseSchema, Nested
from wazo_confd.helpers.restful import ConfdResource

REGISTER_ERROR = "The 'register' key can only be defined in trunk options"


class IAXGeneralOption(BaseSchema):
    key = fields.String(
        validate=(Length(max=128), NoneOf(['register'], error=REGISTER_ERROR)),
        required=True,
        attribute='var_name',
    )
    value = fields.String(validate=Length(max=255), required=True, attribute='var_val')


class IAXGeneralOrderedOption(IAXGeneralOption):
    @pre_load
    def add_envelope(self, data, **kwargs):
        if isinstance(data, list) and len(data) == 2:
            return {'key': data[0], 'value': data[1]}
        return data

    @post_dump
    def remove_envelope(self, data, **kwargs):
        return [data['key'], data['value']]


class IAXGeneralSchema(BaseSchema):
    options = Nested(IAXGeneralOption, many=True, required=True)

    ordered_options = fields.List(Nested(IAXGeneralOrderedOption), required=True)

    @pre_load
    def convert_options_to_collection(self, data, **kwargs):
        options = data.get('options')
        if isinstance(options, dict):
            data['options'] = [
                {'key': key, 'value': value} for key, value in options.items()
            ]
        return data

    @post_load
    def merge_options_and_ordered_options(self, data, **kwargs):
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
    def separate_options_and_ordered_options(self, data, **kwargs):
        return {
            'options': [option for option in data if option.metric is None],
            'ordered_options': [option for option in data if option.metric is not None],
        }

    @post_dump
    def convert_options_to_dict(self, data, **kwargs):
        data['options'] = {option['key']: option['value'] for option in data['options']}
        return data


class IAXGeneralList(ConfdResource):
    model = StaticIAX
    schema = IAXGeneralSchema

    def __init__(self, service):
        super().__init__()
        self.service = service

    @required_master_tenant()
    @required_acl('confd.asterisk.iax.general.get')
    def get(self):
        options = self.service.list()
        return self.schema().dump(options)

    @required_master_tenant()
    @required_acl('confd.asterisk.iax.general.update')
    def put(self):
        form = self.schema().load(request.get_json())
        iax_general = [StaticIAX(**option) for option in form]
        self.service.edit(iax_general)
        return '', 204
