# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource
from wazo_confd.plugins.voicemail.resource import VoicemailList

from ..voicemail.schema import VoicemailSchema


class UserVoicemailItem(ConfdResource):

    has_tenant_uuid = True

    def __init__(self,  user_voicemail_association_middleware):
        super().__init__()

        self._user_voicemail_association_middleware=user_voicemail_association_middleware

    @required_acl('confd.users.{user_id}.voicemails.{voicemail_id}.update')
    def put(self, user_id, voicemail_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._user_voicemail_association_middleware.associate(user_id, voicemail_id,tenant_uuids)
        return '', 204


class UserVoicemailList(ConfdResource):

    schema = VoicemailSchema
    has_tenant_uuid = True

    def __init__(self, service, voicemail_service, user_dao, voicemail_dao, voicemail_middleware,user_voicemail_association_middleware):
        super().__init__()
        self.service = service
        self.user_dao = user_dao
        self.voicemail_dao = voicemail_dao
        self._voicemail_list_resource = VoicemailList(voicemail_service, voicemail_middleware)
        self._user_voicemail_item_resource = UserVoicemailItem(
            user_voicemail_association_middleware
        )
        self._voicemail_middleware=voicemail_middleware
        self._user_voicemail_association_middleware=user_voicemail_association_middleware

    def build_headers(self, voicemail):
        return {'Location': url_for('voicemails', id=voicemail['id'], _external=True)}

    @required_acl('confd.users.{user_id}.voicemails.create')
    def post(self, user_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        voicemail = self._user_voicemail_association_middleware.create_voicemail(
            user_id,
            request.get_json(),
            tenant_uuids,
        )
        return voicemail, 201, self.build_headers(voicemail)

    @required_acl('confd.users.{user_id}.voicemails.read')
    def get(self, user_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids)
        voicemail = self.voicemail_dao.find(user.voicemail_id)
        items = [voicemail] if voicemail else []
        items = self.schema().dump(items, many=True)
        return {'total': len(items), 'items': items}

    @required_acl('confd.users.{user_id}.voicemails.delete')
    def delete(self, user_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids)

        self.service.dissociate_all_by_user(user)
        return '', 204
