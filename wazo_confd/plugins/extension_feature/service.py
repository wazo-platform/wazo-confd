# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.extension import dao as extension_dao

from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


class ExtensionService(CRUDService):

    def search(self, parameters):
        parameters['is_feature'] = True
        return self.dao.search(**parameters)

    def get(self, resource_id):
        return self.dao.get_by(id=resource_id, is_feature=True)

    def edit(self, resource, updated_fields=None):
        with Session.no_autoflush:
            self.validator.validate_edit(resource)
        self.dao.edit(resource)
        self.notifier.edited(resource, updated_fields)


def build_service():
    return ExtensionService(extension_dao,
                            build_validator(),
                            build_notifier())
