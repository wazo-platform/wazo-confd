# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao


class UserVoicemailMiddleware:
    def __init__(self, service, middleware_handle):
        self._service = service
        self._middleware_handle = middleware_handle

    def associate(self, user_id, voicemail_id, tenant_uuids):
        user = user_dao.get_by_id_uuid(user_id, tenant_uuids)
        voicemail = voicemail_dao.get(voicemail_id, tenant_uuids=tenant_uuids)
        self._service.associate(user, voicemail)

    def create_voicemail(self, user_id, body, tenant_uuids):
        voicemail_middleware = self._middleware_handle.get('voicemail')
        voicemail = voicemail_middleware.create(body, tenant_uuids)
        self.associate(user_id, voicemail['id'], tenant_uuids)
        return voicemail
