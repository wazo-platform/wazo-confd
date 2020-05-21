# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource

from .schema import UserFallbackSchema


class UserFallbackList(ConfdResource):

    schema = UserFallbackSchema

    def __init__(self, service, user_dao):
        super().__init__()
        self.service = service
        self.user_dao = user_dao

    @required_acl('confd.users.{user_id}.fallbacks.read')
    def get(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        return self.schema().dump(user.fallbacks)

    @required_acl('confd.users.{user_id}.fallbacks.update')
    def put(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        fallbacks = self.schema().load(request.get_json())
        self.service.edit(user, fallbacks)
        return '', 204
