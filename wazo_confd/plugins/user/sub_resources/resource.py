# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource
from wazo_confd.plugins.user.sub_resources.schema import (
    ServiceDNDSchema,
    ServiceIncallFilterSchema,
    ServicesSchema,
    ForwardBusySchema,
    ForwardNoAnswerSchema,
    ForwardUnconditionalSchema,
    ForwardsSchema)


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
