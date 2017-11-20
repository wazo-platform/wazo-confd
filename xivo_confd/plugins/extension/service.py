# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.extension import dao

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.plugins.extension import validator, notifier
from xivo_confd.plugins.device import builder as device_builder


class ExtensionService(CRUDService):

    def __init__(self, dao, validator, notifier, device_updater):
        super(ExtensionService, self).__init__(dao, validator, notifier)
        self.device_updater = device_updater

    def edit(self, extension, updated_fields=None):
        with Session.no_autoflush:
            self.validator.validate_edit(extension)
        self.dao.edit(extension)
        self.notifier.edited(extension, updated_fields)

        if updated_fields is None or updated_fields:
            self.device_updater.update_for_extension(extension)


def build_service(provd_client):
    device_updater = device_builder.build_device_updater(provd_client)
    return ExtensionService(dao,
                            validator.build_validator(),
                            notifier.build_notifier(),
                            device_updater)
