# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.agent import dao as agent_dao
from xivo_dao.resources.queue import dao as queue_dao
from xivo_dao.resources.user import dao as user_dao

from .resource import (
    QueueMemberAgentItem,
    QueueMemberAgentListLegacy,
    QueueMemberUserItem,
)
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            QueueMemberAgentItem,
            '/queues/<int:queue_id>/members/agents/<int:agent_id>',
            endpoint='queue_member_agents',
            resource_class_args=(service, queue_dao, agent_dao)
        )

        api.add_resource(
            QueueMemberUserItem,
            '/queues/<int:queue_id>/members/users/<uuid:user_id>',
            '/queues/<int:queue_id>/members/users/<int:user_id>',
            endpoint='queue_member_users',
            resource_class_args=(service, queue_dao, user_dao)
        )

        api.add_resource(
            QueueMemberAgentListLegacy,
            '/queues/<int:queue_id>/members/agents',
            resource_class_args=(service, queue_dao, agent_dao)
        )
