# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session


class CRUDService:

    def __init__(self, dao, validator, notifier, extra_parameters=None):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier
        self.extra_parameters = extra_parameters or []

    def search(self, parameters, tenant_uuids=None):
        return self.dao.search(tenant_uuids=tenant_uuids, **parameters)

    def get(self, resource_id, **kwargs):
        return self.dao.get(resource_id, **kwargs)

    def find_by(self, **criteria):
        return self.dao.find_by(**criteria)

    def get_by(self, **criteria):
        return self.dao.get_by(**criteria)

    def create(self, resource):
        self.validator.validate_create(resource)
        created_resource = self.dao.create(resource)
        self.notifier.created(created_resource)
        return created_resource

    def edit(self, resource, updated_fields=None):
        with Session.no_autoflush:
            self.validator.validate_edit(resource)
        self.dao.edit(resource)
        self.notifier.edited(resource)

    def delete(self, resource):
        self.validator.validate_delete(resource)
        self.dao.delete(resource)
        self.notifier.deleted(resource)
