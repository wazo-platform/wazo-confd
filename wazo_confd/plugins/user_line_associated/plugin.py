# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.line import dao as line_dao

from .resource import UserLineAssociatedEndpointSipItem


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']

        api.add_resource(
            UserLineAssociatedEndpointSipItem,
            '/users/<uuid:user_uuid>/lines/<int:line_id>/associated/endpoints/sip',
            resource_class_args=(user_dao, line_dao)
        )
