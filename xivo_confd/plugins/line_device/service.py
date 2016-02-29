# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.helpers import errors

from xivo_confd.database import device as device_db

from xivo_confd.plugins.device.builder import build_device_updater
from xivo_confd.plugins.line.service import build_service as build_line_service
from xivo_confd.plugins.line_device.validator import build_validator


class LineDevice(object):

    @classmethod
    def from_line(cls, line):
        return cls(line.id, line.device_id)

    def __init__(self, line_id, device_id):
        self.line_id = line_id
        self.device_id = device_id


class LineDeviceService(object):

    def __init__(self, validator, line_service, device_updater):
        self.validator = validator
        self.line_service = line_service
        self.device_updater = device_updater

    def associate(self, line, device):
        self.validator.validate_association(line, device)
        line.associate_device(device)
        self.line_service.edit(line)
        if line.endpoint == "sccp":
            device_db.associate_sccp_device(line, device)

    def dissociate(self, line, device):
        self.validator.validate_dissociation(line, device)
        line.remove_device()
        self.line_service.edit(line)
        self.device_updater.update_device(device)
        if line.endpoint == "sccp":
            device_db.dissociate_sccp_device(line, device)

    def dissociate_device(self, device):
        for line in self.line_service.find_all_by(device_id=device.id):
            self.dissociate(line, device)

    def get_association_from_line(self, line_id):
        line = self.line_service.get(line_id)
        if not line.device_id:
            raise errors.not_found('LineDevice', line_id=line_id)
        return LineDevice.from_line(line)

    def find_all_associations_from_device(self, device_id):
        lines = self.line_service.find_all_by(device=device_id)
        return [LineDevice.from_line(line) for line in lines]


def build_service(provd_client):
    validator = build_validator()
    updater = build_device_updater(provd_client)
    service = build_line_service(provd_client)
    return LineDeviceService(validator, service, updater)
