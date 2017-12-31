# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.entity import dao as entity_dao

from .resource import UserEntityList, UserEntityItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        api = core['api']
        service = build_service()

        api.add_resource(
            UserEntityItem,
            '/users/<int:user_id>/entities/<int:entity_id>',
            '/users/<uuid:user_id>/entities/<int:entity_id>',
            endpoint='user_entities',
            resource_class_args=(service, user_dao, entity_dao)
        )
        api.add_resource(
            UserEntityList,
            '/users/<int:user_id>/entities',
            '/users/<uuid:user_id>/entities',
            resource_class_args=(service, user_dao, entity_dao)
        )
