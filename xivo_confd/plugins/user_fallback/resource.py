# -*- coding: UTF-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource

from .schema import UserFallbackSchema


class UserFallbackList(ConfdResource):

    schema = UserFallbackSchema

    def __init__(self, service, user_dao):
        super(UserFallbackList, self).__init__()
        self.service = service
        self.user_dao = user_dao

    @required_acl('confd.users.{user_id}.fallbacks.read')
    def get(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        return self.schema().dump(user.fallbacks).data

    @required_acl('confd.users.{user_id}.fallbacks.update')
    def put(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        fallbacks = self.schema().load(request.get_json()).data
        self.service.edit(user, fallbacks)
        return '', 204
