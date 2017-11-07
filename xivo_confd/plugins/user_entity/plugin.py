# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.entity import dao as entity_dao

from xivo_confd import api
from xivo_confd.plugins.user_entity.service import build_service
from xivo_confd.plugins.user_entity.resource import UserEntityList, UserEntityItem


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(UserEntityItem,
                         '/users/<int:user_id>/entities/<int:entity_id>',
                         '/users/<uuid:user_id>/entities/<int:entity_id>',
                         endpoint='user_entities',
                         resource_class_args=(service, user_dao, entity_dao)
                         )
        api.add_resource(UserEntityList,
                         '/users/<int:user_id>/entities',
                         '/users/<uuid:user_id>/entities',
                         resource_class_args=(service, user_dao, entity_dao)
                         )
