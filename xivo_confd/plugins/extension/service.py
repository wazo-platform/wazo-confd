# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.extension import dao as extension_dao_module

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.plugins.device import builder as device_builder

from .notifier import build_notifier
from .validator import build_context_exists_validator, build_validator

logger = logging.getLogger(__name__)


class ExtensionService(CRUDService):

    def __init__(self, dao, validator, context_exists_validator, notifier, device_updater):
        super(ExtensionService, self).__init__(dao, validator, notifier)
        self.device_updater = device_updater
        self.context_exists_validator = context_exists_validator

    def create(self, extension, tenant_uuids):
        logger.debug('creating %s tenant: %s', extension, tenant_uuids)
        self.context_exists_validator.validate(extension, tenant_uuids)
        return super(ExtensionService, self).create(extension)

    def search(self, parameters, tenant_uuids=None):
        parameters['is_feature'] = False
        return self.dao.search(tenant_uuids=tenant_uuids, **parameters)

    def get(self, resource_id, **kwargs):
        return self.dao.get_by(id=resource_id, is_feature=False, **kwargs)

    def edit(self, extension, updated_fields=None, tenant_uuids=None):
        with Session.no_autoflush:
            self.context_exists_validator.validate(extension, tenant_uuids)
            self.validator.validate_edit(extension)
        self.dao.edit(extension)
        self.notifier.edited(extension, updated_fields)

        if updated_fields is None or updated_fields:
            self.device_updater.update_for_extension(extension)


def build_service(provd_client):
    device_updater = device_builder.build_device_updater(provd_client)
    return ExtensionService(extension_dao_module,
                            build_validator(),
                            build_context_exists_validator(),
                            build_notifier(),
                            device_updater)
