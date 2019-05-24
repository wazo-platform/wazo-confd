# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import VoicemailItem, VoicemailList
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            VoicemailList,
            '/voicemails',
            resource_class_args=(service,)
        )

        api.add_resource(
            VoicemailItem,
            '/voicemails/<int:id>',
            endpoint='voicemails',
            resource_class_args=(service,)
        )
