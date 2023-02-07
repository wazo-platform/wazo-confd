# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import VoicemailSchema


class VoicemailList(ListResource):
    schema = VoicemailSchema
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    def build_headers(self, voicemail):
        return {'Location': url_for('voicemails', id=voicemail['id'], _external=True)}

    @required_acl('confd.voicemails.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        voicemail = self._middleware.create(request.get_json(), tenant_uuids)
        return voicemail, 201, self.build_headers(voicemail)

    @required_acl('confd.voicemails.read')
    def get(self):
        return super().get()


class VoicemailItem(ItemResource):
    schema = VoicemailSchema
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    @required_acl('confd.voicemails.{id}.read')
    def get(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        return self._middleware.get(id, tenant_uuids)

    @required_acl('confd.voicemails.{id}.update')
    def put(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        self.parse_and_update(model, **kwargs)
        return '', 204

    @required_acl('confd.voicemails.{id}.delete')
    def delete(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.delete(id, tenant_uuids)
        return '', 204
