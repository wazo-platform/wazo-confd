# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao

from xivo_confd import api
from xivo_confd.plugins.user_agent.service import build_service
from xivo_confd.plugins.user_agent.resource import UserAgentList, UserAgentItem


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(UserAgentItem,
                         '/users/<int:user_id>/agents/<int:agent_id>',
                         '/users/<uuid:user_id>/agents/<int:agent_id>',
                         endpoint='user_agents',
                         resource_class_args=(service, user_dao)
                         )
        api.add_resource(UserAgentList,
                         '/users/<int:user_id>/agents',
                         '/users/<uuid:user_id>/agents',
                         resource_class_args=(service, user_dao)
                         )
