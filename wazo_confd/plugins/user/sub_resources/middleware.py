# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from .schema import ForwardsSchema


class UserForwardMiddleWare:
    def __init__(self, service_forward):
        self._service_forward = service_forward
        self._schema = ForwardsSchema()

    def associate(self, user_id, body):
        user = self._service_forward.get(user_id)

        form = self._schema.load(body)
        for name, value in form.items():
            setattr(user, name, value)
        self._service_forward.edit(user, self._schema)

    def get(self, user_id):
        user = self._service_forward.get(user_id)
        return self._schema.dump(user)
