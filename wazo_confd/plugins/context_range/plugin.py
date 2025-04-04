# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import (
    ContextConferenceRangeList,
    ContextGroupRangeList,
    ContextIncallRangeList,
    ContextQueueRangeList,
    ContextUserRangeList,
)
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            ContextUserRangeList,
            '/contexts/<int:context_id>/ranges/user',
            resource_class_args=(service,),
        )
        api.add_resource(
            ContextGroupRangeList,
            '/contexts/<int:context_id>/ranges/group',
            resource_class_args=(service,),
        )
        api.add_resource(
            ContextQueueRangeList,
            '/contexts/<int:context_id>/ranges/queue',
            resource_class_args=(service,),
        )
        api.add_resource(
            ContextConferenceRangeList,
            '/contexts/<int:context_id>/ranges/conference',
            resource_class_args=(service,),
        )
        api.add_resource(
            ContextIncallRangeList,
            '/contexts/<int:context_id>/ranges/incall',
            resource_class_args=(service,),
        )
