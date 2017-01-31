# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.resources.moh import dao as moh_dao

from xivo_confd.helpers.resource import CRUDService
from .notifier import build_notifier
from .storage import build_storage
from .validator import build_validator


class MohService(CRUDService):

    def __init__(self, dao, validator, notifier, storage):
        super(MohService, self).__init__(dao, validator, notifier)
        self._storage = storage

    def search(self, parameters):
        total, resources = self.dao.search(**parameters)
        for resource in resources:
            self._update_resource(resource)
        return total, resources

    def get(self, resource_id):
        resource = self.dao.get(resource_id)
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
    return MohService(moh_dao,
                      build_validator(),
                      build_notifier(),
                      build_storage())
