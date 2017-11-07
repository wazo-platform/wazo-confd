# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from flask import request

from marshmallow import fields, pre_dump, post_load
from marshmallow.validate import Length

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource

from xivo_dao.alchemy.staticvoicemail import StaticVoicemail


class VoicemailZoneMessagesOption(BaseSchema):
    name = fields.String(required=True, validate=(Length(max=128)))
    timezone = fields.String(required=True)
    message = fields.String(allow_none=True, missing=None)

    @post_load
    def convert_to_sqlalchemy(self, data):
        message = data['message'] if data['message'] else ''
        return {'var_name': data['name'],
                'var_val': '{}|{}'.format(data['timezone'], message)}

    @pre_dump
    def convert_to_api(self, data):
        timezone, message = data.var_val.split('|', 1)
        return {'name': data.var_name,
                'timezone': timezone,
                'message': message if message else None}


class VoicemailZoneMessagesSchema(BaseSchema):
    items = fields.Nested(VoicemailZoneMessagesOption,
                          many=True,
                          required=True)

    @post_load
    def remove_envelope(self, data):
        return data['items']

    @pre_dump
    def add_envelope(self, data):
        return {'items': [option for option in data]}


class VoicemailZoneMessagesList(ConfdResource):

    model = StaticVoicemail
    schema = VoicemailZoneMessagesSchema

    def __init__(self, service):
        super(VoicemailZoneMessagesList, self).__init__()
        self.service = service

    @required_acl('confd.asterisk.voicemail.zonemessages.get')
    def get(self):
        options = self.service.list()
        return self.schema().dump(options).data

    @required_acl('confd.asterisk.voicemail.zonemessages.update')
    def put(self):
        form = self.schema().load(request.get_json()).data
        voicemail_zonemessages = [StaticVoicemail(**option) for option in form]
        self.service.edit(voicemail_zonemessages)
        return '', 204
