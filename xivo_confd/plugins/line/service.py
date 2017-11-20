# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.line import dao

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.plugins.line.validator import build_validator
from xivo_confd.plugins.line.notifier import build_notifier
from xivo_confd.plugins.device import builder as device_builder
from xivo_confd.plugins.line_device.service import build_service as line_device_build_service
from xivo_confd.plugins.user_line.service import build_service as user_line_build_service
from xivo_dao.helpers.db_manager import Session


class LineService(CRUDService):

    def __init__(self, dao, validator, notifier, device_updater, device_dao, user_line_service, line_device_service):
        super(LineService, self).__init__(dao, validator, notifier)
        self.device_updater = device_updater
        self.device_dao = device_dao
        self.user_line_service = user_line_service
        self.line_device_service = line_device_service

    def find_by(self, **criteria):
        return self.dao.find_by(**criteria)

    def find_all_by(self, **criteria):
        return self.dao.find_all_by(**criteria)

    def edit(self, line, updated_fields=None):
        with Session.no_autoflush:
            self.validator.validate_edit(line)
        self.dao.edit(line)
        self.notifier.edited(line, updated_fields)
        self.device_updater.update_for_line(line)

    def delete(self, line):
        self.validator.validate_delete(line)
        if line.device_id:
            device = self.device_dao.get(line.device_id)
            self.line_device_service.dissociate(line, device)
        for user in line.users:
            self.user_line_service.dissociate(user, line)
        self.dao.delete(line)
        self.notifier.deleted(line)


def build_service(provd_client):
    device_dao = device_builder.build_dao(provd_client)
    device_updater = device_builder.build_device_updater(provd_client)

    return LineService(dao,
                       build_validator(device_dao),
                       build_notifier(),
                       device_updater,
                       device_dao,
                       user_line_build_service(),
                       line_device_build_service(provd_client))
