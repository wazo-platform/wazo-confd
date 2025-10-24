# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields, post_dump, pre_load
from marshmallow.validate import Length
from xivo_dao.alchemy.staticqueue import StaticQueue

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.mallow import BaseSchema, Nested
from wazo_confd.helpers.restful import ConfdResource


class QueueGeneralOption(BaseSchema):
    key = fields.String(validate=(Length(max=128)), required=True, attribute='var_name')
    value = fields.String(required=True, attribute='var_val')


class QueueGeneralSchema(BaseSchema):
    options = Nested(QueueGeneralOption, many=True, required=True)

    @pre_load
    def convert_options_to_collection(self, data, **kwargs):
        options = data.get('options')
        if isinstance(options, dict):
            data['options'] = [
                {'key': key, 'value': value} for key, value in options.items()
            ]
        return data

    @post_dump
    def convert_options_to_dict(self, data, **kwargs):
        data['options'] = {option['key']: option['value'] for option in data['options']}
        return data


class QueueGeneralList(ConfdResource):
    model = StaticQueue
    schema = QueueGeneralSchema

    def __init__(self, service):
        super().__init__()
        self.service = service

    @required_master_tenant()
    @required_acl('confd.asterisk.queue.general.get')
    def get(self):
        options = self.service.list()
        return self.schema().dump({'options': options})

    @required_master_tenant()
    @required_acl('confd.asterisk.queue.general.update')
    def put(self):
        form = self.schema().load(request.get_json(force=True))
        queue_general = [StaticQueue(**option) for option in form['options']]
        self.service.edit(queue_general)
        return '', 204
