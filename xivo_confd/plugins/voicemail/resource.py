# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from flask import url_for
from marshmallow import fields, post_dump
from marshmallow.validate import Regexp, Length

from xivo_dao.resources.voicemail.model import Voicemail

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean
from xivo_confd.helpers.restful import ListResource, ItemResource
from xivo_confd.helpers.validator import LANGUAGE_REGEX

NUMBER_REGEX = r"^[0-9]{1,40}$"
PASSWORD_REGEX = r"^[0-9]{1,80}$"


class VoicemailSchema(BaseSchema):
    id = fields.Integer(dump_only=True)

    name = fields.String(validate=Length(max=80), required=True)
    number = fields.String(validate=Regexp(NUMBER_REGEX), required=True)
    context = fields.String(required=True)

    password = fields.String(validate=Regexp(PASSWORD_REGEX), allow_none=True)
    email = fields.String(validate=Length(max=80), allow_none=True)
    language = fields.String(validate=Regexp(LANGUAGE_REGEX), allow_none=True)
    timezone = fields.String(allow_none=True)
    pager = fields.String(validate=Length(max=80), allow_none=True)
    max_messages = fields.Integer(allow_none=True)
    attach_audio = StrictBoolean(allow_none=True)
    delete_messages = StrictBoolean()
    ask_password = StrictBoolean()
    enabled = StrictBoolean()
    options = fields.List(fields.List(fields.String(), validate=Length(equal=2)))

    @post_dump
    def generate_links(self, output):
        endpoint = 'voicemails'
        output['links'] = [{'href': url_for(endpoint, id=output['id'], _external=True),
                            'rel': endpoint}]
        return output


class VoicemailList(ListResource):

    model = Voicemail
    schema = VoicemailSchema()

    def build_headers(self, voicemail):
        return {'Location': url_for('voicemails', id=voicemail.id, _external=True)}

    @required_acl('confd.voicemails.create')
    def post(self):
        return super(VoicemailList, self).post()

    @required_acl('confd.voicemails.read')
    def get(self):
        return super(VoicemailList, self).get()


class VoicemailItem(ItemResource):

    schema = VoicemailSchema()

    @required_acl('confd.voicemails.{id}.read')
    def get(self, id):
        return super(VoicemailItem, self).get(id)

    @required_acl('confd.voicemails.{id}.update')
    def put(self, id):
        return super(VoicemailItem, self).put(id)

    @required_acl('confd.voicemails.{id}.delete')
    def delete(self, id):
        return super(VoicemailItem, self).delete(id)
