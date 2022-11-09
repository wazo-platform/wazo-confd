# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.userfeatures import UserFeatures as User

from .schema import UserSchemaNullable


class UserMiddleWare:
    def __init__(self, service):
        self._service = service
        self._schema = UserSchemaNullable()

    def create(self, body, tenant_uuid):
        form = self._schema.load(body)
        form['tenant_uuid'] = tenant_uuid
        model = User(**form)
        model = self._service.create(model)
        return self._schema.dump(model)

    def delete(self, user_id, tenant_uuids):
        user = self._service.get(user_id, tenant_uuids=tenant_uuids)
        self._service.delete(user)
