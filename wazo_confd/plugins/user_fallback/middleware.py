# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from xivo_dao.resources.user import dao as user_dao

from wazo_confd.plugins.user_fallback.schema import UserFallbackSchema


class UserFallbackMiddleWare:
    def __init__(self,user_fallback_service  ):
        self._user_fallback_service=user_fallback_service
        self._schema = UserFallbackSchema()

    def associate(self, user_id,body):
        user = user_dao.get_by_id_uuid(user_id)
        fallbacks = self._schema.load(body)
        self._user_fallback_service.edit(user, fallbacks)

    def get(self, user_id):
        user = user_dao.get_by_id_uuid(user_id)
        return self._schema.dump(user.fallbacks)
