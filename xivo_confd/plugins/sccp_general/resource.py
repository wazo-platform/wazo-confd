# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from marshmallow import fields, post_dump, pre_load
from marshmallow.validate import Length

from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource


class SCCPGeneralOptionSchema(BaseSchema):
    key = fields.String(validate=(Length(max=80)),
                        required=True,
                        attribute='option_name')
    value = fields.String(validate=(Length(max=80)),
                          required=True,
                          attribute='option_value')


class SCCPGeneralSchema(BaseSchema):
    options = fields.Nested(SCCPGeneralOptionSchema,
                            many=True,
                            required=True)

    @pre_load
    def convert_options_to_collection(self, data):
        options = data.get('options')
        if isinstance(options, dict):
            data['options'] = [{'key': key, 'value': value} for key, value in options.items()]
        return data

    @post_dump
    def convert_options_to_dict(self, data):
        data['options'] = {option['key']: option['value'] for option in data['options']}
        return data


class SCCPGeneralList(ConfdResource):

    model = SCCPGeneralSettings
    schema = SCCPGeneralSchema

    def __init__(self, service):
        super(SCCPGeneralList, self).__init__()
        self.service = service

    @required_acl('confd.asterisk.sccp.general.get')
    def get(self):
        options = self.service.list()
        return self.schema().dump({'options': options}).data

    @required_acl('confd.asterisk.sccp.general.update')
    def put(self):
        form = self.schema().load(request.get_json()).data
        sccp_general = [self.model(**option) for option in form['options']]
        self.service.edit(sccp_general)
        return '', 204
