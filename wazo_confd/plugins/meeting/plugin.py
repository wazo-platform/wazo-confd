# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import MeetingList, MeetingItem
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']

        service = build_service()

        api.add_resource(
            MeetingList,
            '/meetings',
            resource_class_args=(service,),
        )
        api.add_resource(
            MeetingItem,
            '/meetings/<uuid:uuid>',
            endpoint='meetings',
            resource_class_args=(service,),
        )
