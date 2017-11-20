# -*- coding: UTF-8 -*-
# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
