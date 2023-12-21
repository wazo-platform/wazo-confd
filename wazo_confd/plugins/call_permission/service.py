# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.call_permission import dao as call_permission_dao
from xivo_dao.resources.call_permission import strategy

from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


class CallPermissionService(CRUDService):
    def create(self, call_permission):
        self.validator.validate_create(
            call_permission, tenant_uuids=[call_permission.tenant_uuid]
        )
        created_call_permission = self.dao.create(call_permission)
        self.notifier.created(created_call_permission)
        return created_call_permission

    def edit(self, call_permission, updated_fields=None):
        with Session.no_autoflush:
            self.validator.validate_edit(
                call_permission, tenant_uuids=[call_permission.tenant_uuid]
            )
        self.dao.edit(call_permission)
        self.notifier.edited(call_permission)

    @call_permission_dao.query_options(*strategy.preload_relationships)
    def get(self, resource_id, **kwargs):
        return super().get(resource_id, **kwargs)

    @call_permission_dao.query_options(*strategy.preload_relationships)
    def search(self, parameters, tenant_uuids=None):
        return super().search(parameters, tenant_uuids)


def build_service():
    return CallPermissionService(
        call_permission_dao, build_validator(), build_notifier()
    )
