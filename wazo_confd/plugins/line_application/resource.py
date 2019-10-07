# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class LineApplicationAssociation(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, line_dao, application_dao, service):
        self.line_dao = line_dao
        self.application_dao = application_dao
        self.service = service

    @required_acl('confd.lines.{line_id}.applications.{application_uuid}.update')
    def put(self, line_id, application_uuid):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)
        application = self.application_dao.get(
            application_uuid, tenant_uuids=tenant_uuids
        )
        self.service.associate(line, application)
        return '', 204

    @required_acl('confd.lines.{line_id}.applications.{application_uuid}.delete')
    def delete(self, line_id, application_uuid):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)
        application = self.application_dao.get(
            application_uuid, tenant_uuids=tenant_uuids
        )
        self.service.dissociate(line, application)
        return '', 204
