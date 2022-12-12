# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao

from wazo_confd.plugins.voicemail.service import (
    build_service as build_voicemail_service,
)
from .middleware import UserVoicemailMiddleware

from .resource import (
    UserVoicemailItem,
    UserVoicemailList,
)
from .service import build_service
from ..voicemail.middleware import VoicemailMiddleWare


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        middleware_handle = dependencies['middleware_handle']
        service = build_service()
        voicemail_service = build_voicemail_service()


        user_voicemail_association_middleware = UserVoicemailMiddleware(service)
        middleware_handle.register('user_voicemail_association', user_voicemail_association_middleware)


        try:
            voicemail_middleware = middleware_handle.get('voicemail')
        except KeyError:
            voicemail_middleware = VoicemailMiddleWare(voicemail_service)
        middleware_handle.register('voicemail', voicemail_middleware)

        api.add_resource(
            UserVoicemailList,
            '/users/<int:user_id>/voicemails',
            '/users/<uuid:user_id>/voicemails',
            endpoint='user_voicemails',
            resource_class_args=(service, voicemail_service, user_dao, voicemail_dao, voicemail_middleware,user_voicemail_association_middleware,),
        )

        api.add_resource(
            UserVoicemailItem,
            '/users/<int:user_id>/voicemails/<int:voicemail_id>',
            '/users/<uuid:user_id>/voicemails/<int:voicemail_id>',
            resource_class_args=( user_voicemail_association_middleware,),
        )
