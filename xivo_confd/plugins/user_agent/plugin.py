# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.agent import dao as agent_dao
from xivo_dao.resources.user import dao as user_dao

from .resource import UserAgentList, UserAgentItem
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            UserAgentItem,
            '/users/<int:user_id>/agents/<int:agent_id>',
            '/users/<uuid:user_id>/agents/<int:agent_id>',
            endpoint='user_agents',
            resource_class_args=(service, user_dao, agent_dao)
        )
        api.add_resource(
            UserAgentList,
            '/users/<int:user_id>/agents',
            '/users/<uuid:user_id>/agents',
            resource_class_args=(service, user_dao)
        )
