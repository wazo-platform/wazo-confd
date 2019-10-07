# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.moh import dao as moh_dao

from wazo_confd.helpers.resource import CRUDService
from .notifier import build_notifier
from .storage import build_storage
from .validator import build_validator


class MohService(CRUDService):
    def __init__(self, dao, validator, notifier, storage):
        super(MohService, self).__init__(dao, validator, notifier)
        self._storage = storage

    def search(self, parameters, tenant_uuids=None):
        total, resources = self.dao.search(tenant_uuids=tenant_uuids, **parameters)
        for resource in resources:
            self._update_resource(resource)
        return total, resources

    def get(self, resource_id, tenant_uuids=None):
        resource = self.dao.get(resource_id, tenant_uuids=tenant_uuids)
        self._update_resource(resource)
        return resource

    def create(self, resource):
        self.validator.validate_create(resource)
        created_resource = self.dao.create(resource)
        self._storage.create_directory(created_resource)
        self._update_resource(created_resource)
        self.notifier.created(created_resource)
        return created_resource

    def delete(self, resource):
        self.validator.validate_delete(resource)
        self.dao.delete(resource)
        self._storage.remove_directory(resource)
        self.notifier.deleted(resource)

    def load_file(self, resource, filename):
        return self._storage.load_file(resource, filename)

    def save_file(self, resource, filename, content):
        self._storage.save_file(resource, filename, content)
        self.notifier.files_changed(resource)

    def delete_file(self, resource, filename):
        self._storage.remove_file(resource, filename)
        self.notifier.files_changed(resource)

    def _update_resource(self, resource):
        resource.files = self._storage.list_files(resource)


def build_service():
    return MohService(moh_dao, build_validator(), build_notifier(), build_storage())
