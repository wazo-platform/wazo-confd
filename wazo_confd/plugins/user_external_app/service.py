# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.external_app import dao as external_app_dao
from xivo_dao.resources.user_external_app import dao as user_external_app_dao
from xivo_dao.helpers.db_manager import Session

from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


class UserExternalAppService(CRUDService):
    def __init__(self, dao, external_app_dao, validator, notifier):
        self.dao = dao
        self.external_app_dao = external_app_dao
        self.validator = validator
        self.notifier = notifier

    def search(self, user_uuid, tenant_uuid, parameters):
        if 'fallback' == parameters.get('view'):
            # NOTE(fblackburn): pagination and sorting are disabled with fallback
            _, result_by_user = self.dao.search(user_uuid)
            params = {'tenant_uuids': [tenant_uuid]}
            _, result_by_tenant = self.external_app_dao.search(**params)
            result = {app.name: app for app in result_by_tenant + result_by_user}
            return len(result.values()), result.values()

        return self.dao.search(user_uuid, **parameters)

    def get(self, user_uuid, tenant_uuid, name, view=None):
        result = self.dao.find(user_uuid, name)
        if result:
            return result

        if view == 'fallback':
            result = self.external_app_dao.find(name, tenant_uuids=[tenant_uuid])
            if result:
                return result

        raise errors.not_found('UserExternalApp', name=name)

    def create(self, app, tenant_uuid):
        self.validator.validate_create(app)
        created_resource = self.dao.create(app)
        self.notifier.created(created_resource, tenant_uuid)
        return created_resource

    def edit(self, app, updated_fields=None, tenant_uuid=None):
        with Session.no_autoflush:
            self.validator.validate_edit(app)
        self.dao.edit(app)
        self.notifier.edited(app, tenant_uuid)

    def delete(self, app, tenant_uuid):
        self.validator.validate_delete(app)
        self.dao.delete(app)
        self.notifier.deleted(app, tenant_uuid)


def build_service():
    return UserExternalAppService(
        user_external_app_dao,
        external_app_dao,
        build_validator(),
        build_notifier(),
    )
