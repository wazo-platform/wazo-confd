# -*- coding: UTF-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.resources.extension import dao as extension_dao

from .notifier import build_notifier
from .validator import build_validator


class ParkingLotExtensionService(object):

    def __init__(self, extension_dao, notifier, validator):
        self.extension_dao = extension_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, parking_lot, extension):
        self.validator.validate_association(parking_lot, extension)
        self.extension_dao.associate_parking_lot(parking_lot, extension)
        self.notifier.associated(parking_lot, extension)

    def dissociate(self, parking_lot, extension):
        self.validator.validate_dissociation(parking_lot, extension)
        self.extension_dao.dissociate_parking_lot(parking_lot, extension)
        self.notifier.dissociated(parking_lot, extension)


def build_service():
    return ParkingLotExtensionService(extension_dao,
                                      build_notifier(),
                                      build_validator())
