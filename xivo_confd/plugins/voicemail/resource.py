# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo_dao.alchemy.voicemail import Voicemail

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import VoicemailSchema


class VoicemailList(ListResource):

    model = Voicemail
    schema = VoicemailSchema
    has_tenant_uuid = True

    def build_headers(self, voicemail):
        return {'Location': url_for('voicemails', id=voicemail.id, _external=True)}

    @required_acl('confd.voicemails.create')
    def post(self):
        form = self.schema().load(request.get_json()).data
        model = self.model(**form)
        tenant_uuids = self._build_tenant_list({'recurse': True})
        model = self.service.create(model, tenant_uuids)
        return self.schema().dump(model).data, 201, self.build_headers(model)

    @required_acl('confd.voicemails.read')
    def get(self):
        return super(VoicemailList, self).get()


class VoicemailItem(ItemResource):

    schema = VoicemailSchema
    has_tenant_uuid = True

    @required_acl('confd.voicemails.{id}.read')
    def get(self, id):
        return super(VoicemailItem, self).get(id)

    @required_acl('confd.voicemails.{id}.update')
    def put(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        self.parse_and_update(model, **kwargs)
        return '', 204

    @required_acl('confd.voicemails.{id}.delete')
    def delete(self, id):
        return super(VoicemailItem, self).delete(id)
