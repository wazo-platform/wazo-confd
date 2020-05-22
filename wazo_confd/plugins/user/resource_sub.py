# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import EXCLUDE, fields, pre_dump, post_load
from marshmallow.validate import Length

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean
from wazo_confd.helpers.restful import ConfdResource


class UserSubResource(ConfdResource):
    def __init__(self, service):
        self.service = service

    def get(self, user_id):
        user = self.service.get(user_id)
        return self.schema().dump(user)

    def put(self, user_id):
        user = self.service.get(user_id)
        self.parse_and_update(user)
        return '', 204

    def parse_and_update(self, model):
        form = self.schema().load(request.get_json())
        for name, value in form.items():
            setattr(model, name, value)
        self.service.edit(model, self.schema())


class ServiceDNDSchema(BaseSchema):
    enabled = StrictBoolean(attribute='dnd_enabled', required=True)

    types = ['dnd']


class ServiceIncallFilterSchema(BaseSchema):
    enabled = StrictBoolean(attribute='incallfilter_enabled', required=True)

    types = ['incallfilter']


class ServicesSchema(BaseSchema):
    dnd = fields.Nested(ServiceDNDSchema, unknown=EXCLUDE)
    incallfilter = fields.Nested(ServiceIncallFilterSchema, unknown=EXCLUDE)

    types = ['dnd', 'incallfilter']

    @pre_dump()
    def add_envelope(self, data):
        return {type_: data for type_ in self.types}

    @post_load
    def remove_envelope(self, data):
        result = {}
        for service in data.values():
            for key, value in service.items():
                result[key] = value
        return result


class UserServiceDND(UserSubResource):

    schema = ServiceDNDSchema

    @required_acl('confd.users.{user_id}.services.dnd.read')
    def get(self, user_id):
        return super().get(user_id)

    @required_acl('confd.users.{user_id}.services.dnd.update')
    def put(self, user_id):
        return super().put(user_id)


class UserServiceIncallFilter(UserSubResource):

    schema = ServiceIncallFilterSchema

    @required_acl('confd.users.{user_id}.services.dnd.read')
    def get(self, user_id):
        return super().get(user_id)

    @required_acl('confd.users.{user_id}.services.dnd.update')
    def put(self, user_id):
        return super().put(user_id)


class UserServiceList(UserSubResource):

    schema = ServicesSchema

    @required_acl('confd.users.{user_id}.services.read')
    def get(self, user_id):
        return super().get(user_id)

    @required_acl('confd.users.{user_id}.services.update')
    def put(self, user_id):
        return super().put(user_id)


class ForwardBusySchema(BaseSchema):
    enabled = StrictBoolean(attribute='busy_enabled')
    destination = fields.String(
        attribute='busy_destination', validate=Length(max=128), allow_none=True
    )

    types = ['busy']


class ForwardNoAnswerSchema(BaseSchema):
    enabled = StrictBoolean(attribute='noanswer_enabled')
    destination = fields.String(
        attribute='noanswer_destination', validate=Length(max=128), allow_none=True
    )

    types = ['noanswer']


class ForwardUnconditionalSchema(BaseSchema):
    enabled = StrictBoolean(attribute='unconditional_enabled')
    destination = fields.String(
        attribute='unconditional_destination', validate=Length(max=128), allow_none=True
    )

    types = ['unconditional']


class ForwardsSchema(BaseSchema):
    busy = fields.Nested(ForwardBusySchema, unknown=EXCLUDE)
    noanswer = fields.Nested(ForwardNoAnswerSchema, unknown=EXCLUDE)
    unconditional = fields.Nested(ForwardUnconditionalSchema, unknown=EXCLUDE)

    types = ['busy', 'noanswer', 'unconditional']

    @pre_dump
    def add_envelope(self, data):
        return {type_: data for type_ in self.types}

    @post_load
    def remove_envelope(self, data):
        result = {}
        for forward in data.values():
            for key, value in forward.items():
                result[key] = value
        return result


class UserForwardBusy(UserSubResource):

    schema = ForwardBusySchema

    @required_acl('confd.users.{user_id}.forwards.busy.read')
    def get(self, user_id):
        return super().get(user_id)

    @required_acl('confd.users.{user_id}.forwards.busy.update')
    def put(self, user_id):
        return super().put(user_id)


class UserForwardNoAnswer(UserSubResource):

    schema = ForwardNoAnswerSchema

    @required_acl('confd.users.{user_id}.forwards.noanswer.read')
    def get(self, user_id):
        return super().get(user_id)

    @required_acl('confd.users.{user_id}.forwards.noanswer.update')
    def put(self, user_id):
        return super().put(user_id)


class UserForwardUnconditional(UserSubResource):

    schema = ForwardUnconditionalSchema

    @required_acl('confd.users.{user_id}.forwards.unconditional.read')
    def get(self, user_id):
        return super().get(user_id)

    @required_acl('confd.users.{user_id}.forwards.unconditional.update')
    def put(self, user_id):
        return super().put(user_id)


class UserForwardList(UserSubResource):

    schema = ForwardsSchema

    @required_acl('confd.users.{user_id}.forwards.read')
    def get(self, user_id):
        return super().get(user_id)

    @required_acl('confd.users.{user_id}.forwards.update')
    def put(self, user_id):
        return super().put(user_id)
