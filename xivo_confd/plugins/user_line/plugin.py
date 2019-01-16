# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.line import dao as line_dao

from .resource import UserLineList, UserLineItem, LineUserList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            UserLineItem,
            '/users/<int:user_id>/lines/<int:line_id>',
            '/users/<uuid:user_id>/lines/<int:line_id>',
            endpoint='user_lines',
            resource_class_args=(service, user_dao, line_dao)
        )
        api.add_resource(
            UserLineList,
            '/users/<int:user_id>/lines',
            '/users/<uuid:user_id>/lines',
            resource_class_args=(service, user_dao, line_dao)
        )
        api.add_resource(
            LineUserList,
            '/lines/<int:line_id>/users',
            resource_class_args=(service, user_dao, line_dao)
        )
