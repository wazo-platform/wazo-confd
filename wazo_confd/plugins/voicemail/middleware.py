# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.voicemail import Voicemail

from .schema import VoicemailSchema


class VoicemailMiddleWare:
    def __init__(self, service):
        self._service = service
        self._schema = VoicemailSchema()

    def create(self, body, tenant_uuids):
        form = self._schema.load(body)
        model = Voicemail(**form)
        model = self._service.create(model, tenant_uuids)
        return self._schema.dump(model)

    def delete(self, voicemail_id, tenant_uuids):
        voicemail = self._service.get(voicemail_id, tenant_uuids=tenant_uuids)
        self._service.delete(voicemail)
