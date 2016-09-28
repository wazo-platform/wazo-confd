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
from marshmallow import fields, pre_dump, post_load

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean
from xivo_confd.helpers.restful import ConfdResource


class UserSubResource(ConfdResource):

    def __init__(self, service):
        self.service = service

    def get(self, user_id):
        user = self.service.get(user_id)
        return self.schema().dump(user).data

    def put(self, user_id):
        user = self.service.get(user_id)
        self.parse_and_update(user)
        return '', 204

    def parse_and_update(self, model):
        form = self.schema().load(request.get_json()).data
        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model, self.schema())


class ServiceDNDSchema(BaseSchema):
    enabled = StrictBoolean(attribute='dnd_enabled', required=True)

    types = ['dnd']


class ServiceIncallFilterSchema(BaseSchema):
    enabled = StrictBoolean(attribute='incallfilter_enabled', required=True)

    types = ['incallfilter']


class ServicesSchema(BaseSchema):
    dnd = fields.Nested(ServiceDNDSchema)
    incallfilter = fields.Nested(ServiceIncallFilterSchema)

    types = ['dnd', 'incallfilter']

    @pre_dump()
    def add_envelope(self, data):
        return {type_: data for type_ in self.types}


class UserServiceDND(UserSubResource):

    schema = ServiceDNDSchema

    @required_acl('confd.users.{user_id}.services.dnd.read')
    def get(self, user_id):
        return super(UserServiceDND, self).get(user_id)

    @required_acl('confd.users.{user_id}.services.dnd.update')
    def put(self, user_id):
        return super(UserServiceDND, self).put(user_id)


class UserServiceIncallFilter(UserSubResource):

    schema = ServiceIncallFilterSchema

    @required_acl('confd.users.{user_id}.services.dnd.read')
    def get(self, user_id):
        return super(UserServiceIncallFilter, self).get(user_id)

    @required_acl('confd.users.{user_id}.services.dnd.update')
    def put(self, user_id):
        return super(UserServiceIncallFilter, self).put(user_id)


class UserServiceList(UserSubResource):

    schema = ServicesSchema

    @required_acl('confd.users.{user_id}.services.read')
    def get(self, user_id):
        return super(UserServiceList, self).get(user_id)


class ForwardBusySchema(BaseSchema):
    enabled = StrictBoolean(attribute='busy_enabled')
    destination = fields.String(attribute='busy_destination', allow_none=True)

    types = ['busy']


class ForwardNoAnswerSchema(BaseSchema):
    enabled = StrictBoolean(attribute='noanswer_enabled')
    destination = fields.String(attribute='noanswer_destination', allow_none=True)

    types = ['noanswer']


class ForwardUnconditionalSchema(BaseSchema):
    enabled = StrictBoolean(attribute='unconditional_enabled')
    destination = fields.String(attribute='unconditional_destination', allow_none=True)

    types = ['unconditional']


class ForwardsSchema(BaseSchema):
    busy = fields.Nested(ForwardBusySchema)
    noanswer = fields.Nested(ForwardNoAnswerSchema)
    unconditional = fields.Nested(ForwardUnconditionalSchema)

    types = ['busy', 'noanswer', 'unconditional']

    @pre_dump
    def add_envelope(self, data):
        return {type_: data for type_ in self.types}

    @post_load
    def remove_envelope(self, data):
        result = {}
        for forward in data.itervalues():
            for key, value in forward.iteritems():
                result[key] = value
        return result


class UserForwardBusy(UserSubResource):

    schema = ForwardBusySchema

    @required_acl('confd.users.{user_id}.forwards.busy.read')
    def get(self, user_id):
        return super(UserForwardBusy, self).get(user_id)

    @required_acl('confd.users.{user_id}.forwards.busy.update')
    def put(self, user_id):
        return super(UserForwardBusy, self).put(user_id)


class UserForwardNoAnswer(UserSubResource):

    schema = ForwardNoAnswerSchema

    @required_acl('confd.users.{user_id}.forwards.noanswer.read')
    def get(self, user_id):
        return super(UserForwardNoAnswer, self).get(user_id)

    @required_acl('confd.users.{user_id}.forwards.noanswer.update')
    def put(self, user_id):
        return super(UserForwardNoAnswer, self).put(user_id)


class UserForwardUnconditional(UserSubResource):

    schema = ForwardUnconditionalSchema

    @required_acl('confd.users.{user_id}.forwards.unconditional.read')
    def get(self, user_id):
        return super(UserForwardUnconditional, self).get(user_id)

    @required_acl('confd.users.{user_id}.forwards.unconditional.update')
    def put(self, user_id):
        return super(UserForwardUnconditional, self).put(user_id)


class UserForwardList(UserSubResource):

    schema = ForwardsSchema

    @required_acl('confd.users.{user_id}.forwards.read')
    def get(self, user_id):
        return super(UserForwardList, self).get(user_id)

    @required_acl('confd.users.{user_id}.forwards.update')
    def put(self, user_id):
        return super(UserForwardList, self).put(user_id)
