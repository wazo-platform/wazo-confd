# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from .notifier import build_notifier
from .validator import build_validator

from xivo_dao.resources.extension import dao as extension_dao


class IncallExtensionService(object):

    def __init__(self, extension_dao, notifier, validator):
        self.extension_dao = extension_dao
        self.validator = validator
        self.notifier = notifier

    def get(self, incall, extension):
        return self.extension_dao.get_by(type='incall', typeval=str(incall.id), id=extension.id)

    def associate(self, incall, extension):
        self.validator.validate_association(incall, extension)
        self.extension_dao.associate_incall(incall, extension)
        self.notifier.associated(incall, extension)

    def dissociate(self, incall, extension):
        self.validator.validate_dissociation(incall, extension)
        self.extension_dao.dissociate_incall(incall, extension)
        self.notifier.dissociated(incall, extension)


def build_service():
    return IncallExtensionService(extension_dao,
                                  build_notifier(),
                                  build_validator())
