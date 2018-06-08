# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import QueueMemberAssociation, QueueMemberPost
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            QueueMemberAssociation,
            '/queues/<int:queue_id>/members/agents/<int:agent_id>',
            endpoint='queuemembers',
            resource_class_args=(service,)
        )

        api.add_resource(
            QueueMemberPost,
            '/queues/<int:queue_id>/members/agents',
            resource_class_args=(service,)
        )
