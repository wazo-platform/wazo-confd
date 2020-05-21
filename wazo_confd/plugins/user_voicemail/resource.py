# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class UserVoicemailResource(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, user_dao, voicemail_dao):
        super().__init__()
        self.service = service
        self.user_dao = user_dao
        self.voicemail_dao = voicemail_dao

    def get_user(self, user_id, tenant_uuids=None):
        return self.user_dao.get_by_id_uuid(user_id, tenant_uuids)


class UserVoicemailItem(UserVoicemailResource):
    @required_acl('confd.users.{user_id}.voicemails.{voicemail_id}.update')
    def put(self, user_id, voicemail_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        user = self.get_user(user_id, tenant_uuids=tenant_uuids)
        voicemail = self.voicemail_dao.get(voicemail_id, tenant_uuids=tenant_uuids)

        self.service.associate(user, voicemail)
        return '', 204


class UserVoicemailList(UserVoicemailResource):
    @required_acl('confd.users.{user_id}.voicemails.delete')
    def delete(self, user_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        user = self.get_user(user_id, tenant_uuids=tenant_uuids)

        self.service.dissociate_all_by_user(user)
        return '', 204
