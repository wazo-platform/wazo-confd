# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.entity import dao as entity_dao

from .resource import UserEntityList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            UserEntityList,
            '/users/<int:user_id>/entities',
            '/users/<uuid:user_id>/entities',
            resource_class_args=(service, user_dao, entity_dao)
        )
