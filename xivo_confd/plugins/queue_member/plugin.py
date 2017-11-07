# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.queue_member.resource import QueueMemberAssociation
from xivo_confd.plugins.queue_member.resource import QueueMemberPost

from xivo_confd.plugins.queue_member.service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(QueueMemberAssociation,
                         '/queues/<int:queue_id>/members/agents/<int:agent_id>',
                         endpoint='queuemembers',
                         resource_class_args=(service,)
                         )

        api.add_resource(QueueMemberPost,
                         '/queues/<int:queue_id>/members/agents',
                         resource_class_args=(service,)
                         )
