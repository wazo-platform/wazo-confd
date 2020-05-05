# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao

from .resource import (
    UserVoicemailItem,
    UserVoicemailList,
)
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            UserVoicemailList,
            '/users/<int:user_id>/voicemails',
            '/users/<uuid:user_id>/voicemails',
            endpoint='user_voicemails',
            resource_class_args=(service, user_dao, voicemail_dao),
        )

        api.add_resource(
            UserVoicemailItem,
            '/users/<int:user_id>/voicemails/<int:voicemail_id>',
            '/users/<uuid:user_id>/voicemails/<int:voicemail_id>',
            resource_class_args=(service, user_dao, voicemail_dao),
        )
