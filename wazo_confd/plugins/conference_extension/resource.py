# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class ConferenceExtensionItem(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, conference_dao, extension_dao):
        super(ConferenceExtensionItem, self).__init__()
        self.service = service
        self.conference_dao = conference_dao
        self.extension_dao = extension_dao

    @required_acl('confd.conferences.{conference_id}.extensions.{extension_id}.delete')
    def delete(self, conference_id, extension_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        conference = self.conference_dao.get(conference_id, tenant_uuids=tenant_uuids)
        extension = self.extension_dao.get(extension_id, tenant_uuids=tenant_uuids)

        self.service.dissociate(conference, extension)
        return '', 204

    @required_acl('confd.conferences.{conference_id}.extensions.{extension_id}.update')
    def put(self, conference_id, extension_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        conference = self.conference_dao.get(conference_id, tenant_uuids=tenant_uuids)
        extension = self.extension_dao.get(extension_id, tenant_uuids=tenant_uuids)

        self.service.associate(conference, extension)
        return '', 204
