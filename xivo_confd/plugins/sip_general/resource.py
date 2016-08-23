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

from flask import request
from marshmallow import fields, post_dump, pre_load
from marshmallow.validate import Length

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource

from xivo_dao.alchemy.staticsip import StaticSIP

import logging

logger = logging.getLogger(__name__)


class KeyValueOption(BaseSchema):
    key = fields.String(validate=Length(max=128), required=True, attribute='var_name')
    value = fields.String(validate=Length(max=255), required=True, allow_none=True, attribute='var_val')

    @pre_load
    def add_envelope(self, data):
        if isinstance(data, list) and len(data) == 2:
            return {'key': data[0], 'value': data[1]}

    @post_dump
    def remove_envelope(self, data):
        return [data['key'], data['value']]


class SIPGeneralSchema(BaseSchema):
    options = fields.List(fields.Nested(KeyValueOption),
                          required=True)


class SIPGeneralList(ConfdResource):

    model = StaticSIP
    schema = SIPGeneralSchema()

    def __init__(self, service):
        super(SIPGeneralList, self).__init__()
        self.service = service

    @required_acl('confd.asterisk.sip.general.get')
    def get(self):
        options = self.service.list()
        return self.schema.dump({'options': options}).data

    @required_acl('confd.asterisk.sip.general.update')
    def put(self):
        form = self.schema.load(request.get_json()).data
        sip_general = [StaticSIP(**option) for option in form['options']]
        self.service.edit(sip_general)
        return '', 204
