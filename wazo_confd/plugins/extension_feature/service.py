# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.feature_extension import dao as feature_extension_dao

from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


class FeatureExtensionService(CRUDService):
    def search(self, parameters):
        return self.dao.search(**parameters)

    def get(self, resource_uuid):
        return self.dao.get_by(uuid=resource_uuid)

    def edit(self, resource, updated_fields=None):
        with Session.no_autoflush:
            self.validator.validate_edit(resource)
        self.dao.edit(resource)
        self.notifier.edited(resource, updated_fields)


def build_service():
    return FeatureExtensionService(
        feature_extension_dao, build_validator(), build_notifier()
    )
