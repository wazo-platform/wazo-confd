# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields, post_load, pre_dump
from marshmallow.validate import Length
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.mallow import BaseSchema, Nested
from wazo_confd.helpers.restful import ConfdResource


class VoicemailZoneMessagesOption(BaseSchema):
    name = fields.String(required=True, validate=(Length(max=128)))
    timezone = fields.String(required=True)
    message = fields.String(allow_none=True, load_default=None)

    @post_load
    def convert_to_sqlalchemy(self, data, **kwargs):
        message = data['message'] if data['message'] else ''
        return {
            'var_name': data['name'],
            'var_val': '{}|{}'.format(data['timezone'], message),
        }

    @pre_dump
    def convert_to_api(self, data, **kwargs):
        timezone, message = data.var_val.split('|', 1)
        return {
            'name': data.var_name,
            'timezone': timezone,
            'message': message if message else None,
        }


class VoicemailZoneMessagesSchema(BaseSchema):
    items = Nested(VoicemailZoneMessagesOption, many=True, required=True)

    @post_load
    def remove_envelope(self, data, **kwargs):
        return data['items']

    @pre_dump
    def add_envelope(self, data, **kwargs):
        return {'items': [option for option in data]}


class VoicemailZoneMessagesList(ConfdResource):
    model = StaticVoicemail
    schema = VoicemailZoneMessagesSchema

    def __init__(self, service):
        super().__init__()
        self.service = service

    @required_acl('confd.asterisk.voicemail.zonemessages.get')
    def get(self):
        options = self.service.list()
        return self.schema().dump(options)

    @required_master_tenant()
    @required_acl('confd.asterisk.voicemail.zonemessages.update')
    def put(self):
        form = self.schema().load(request.get_json())
        voicemail_zonemessages = [StaticVoicemail(**option) for option in form]
        self.service.edit(voicemail_zonemessages)
        return '', 204
