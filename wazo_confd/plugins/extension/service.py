# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.extension import dao as extension_dao_module

from wazo_confd.helpers.resource import CRUDService
from wazo_confd.plugins.device import builder as device_builder

from .notifier import build_notifier
from .validator import build_validator

logger = logging.getLogger(__name__)


class ExtensionService(CRUDService):

    def __init__(self, dao, validator, notifier, device_updater):
        super(ExtensionService, self).__init__(dao, validator, notifier)
        self.device_updater = device_updater

    def create(self, extension, tenant_uuids):
        self.validator.validate_create(extension, tenant_uuids)
        created_extension = self.dao.create(extension)
        self.notifier.created(created_extension)
        return created_extension

    def search(self, parameters, tenant_uuids=None):
        parameters['is_feature'] = False
        return self.dao.search(tenant_uuids=tenant_uuids, **parameters)

    def get(self, resource_id, **kwargs):
        return self.dao.get_by(id=resource_id, is_feature=False, **kwargs)

    def edit(self, extension, updated_fields=None, tenant_uuids=None):
        with Session.no_autoflush:
            self.validator.validate_edit(extension, tenant_uuids)
        self.dao.edit(extension)
        self.notifier.edited(extension, updated_fields)

        if updated_fields is None or updated_fields:
            self.device_updater.update_for_extension(extension)


def build_service(provd_client):
    device_updater = device_builder.build_device_updater(provd_client)
    return ExtensionService(extension_dao_module,
                            build_validator(),
                            build_notifier(),
                            device_updater)
