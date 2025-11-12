# Copyright 2022-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.voicemail import Voicemail

from ...middleware import ResourceMiddleware
from .schema import VoicemailSchema


class VoicemailMiddleWare(ResourceMiddleware):
    def __init__(self, service):
        self._service = service
        self._schema = VoicemailSchema()
        self._update_schema = VoicemailSchema()

    def create(self, body, tenant_uuids):
        form = self._schema.load(body)
        accesstype = form.pop('accesstype', 'personal')
        model = Voicemail(**form)
        model.accesstype = accesstype
        model = self._service.create(model, tenant_uuids)
        return self._schema.dump(model)

    def delete(self, voicemail_id, tenant_uuids):
        voicemail = self._service.get(voicemail_id, tenant_uuids=tenant_uuids)
        self._service.delete(voicemail)

    def get(self, voicemail_id, tenant_uuids):
        voicemail = self._service.get(voicemail_id, tenant_uuids=tenant_uuids)
        return self._schema.dump(voicemail)

    def update(self, voicemail_id, body, tenant_uuids):
        model = self._service.get(voicemail_id, tenant_uuids=tenant_uuids)
        self.parse_and_update(model, body, tenant_uuids=tenant_uuids)
