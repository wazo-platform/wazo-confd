# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.resources.line import dao

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.plugins.line.validator import build_validator
from xivo_confd.plugins.line.notifier import build_notifier
from xivo_confd.plugins.device import builder as device_builder
from xivo_dao.helpers.db_manager import Session


class LineService(CRUDService):

    def __init__(self, dao, validator, notifier, device_updater):
        super(LineService, self).__init__(dao, validator, notifier)
        self.device_updater = device_updater

    def find_by(self, **criteria):
        return self.dao.find_by(**criteria)

    def find_all_by(self, **criteria):
        return self.dao.find_all_by(**criteria)

    def edit(self, line, updated_fields=[]):
        with Session.no_autoflush:
            self.validator.validate_edit(line)
        self.dao.edit(line)
        self.notifier.edited(line)
        self.device_updater.update_for_line(line)


def build_service(provd_client):
    device_dao = device_builder.build_dao(provd_client)
    device_updater = device_builder.build_device_updater(provd_client)

    return LineService(dao,
                       build_validator(device_dao),
                       build_notifier(),
                       device_updater)
