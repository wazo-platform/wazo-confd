# -*- coding: UTF-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.extension import dao as extension_dao

from .notifier import build_notifier
from .validator import build_validator


class IncallExtensionService(object):

    def __init__(self, extension_dao, notifier, validator):
        self.extension_dao = extension_dao
        self.validator = validator
        self.notifier = notifier

    def get(self, incall, extension):
        return self.extension_dao.get_by(type='incall', typeval=str(incall.id), id=extension.id)

    def associate(self, incall, extension):
        if extension in incall.extensions:
            return

        self.validator.validate_association(incall, extension)
        self.extension_dao.associate_incall(incall, extension)
        self.notifier.associated(incall, extension)

    def dissociate(self, incall, extension):
        if extension not in incall.extensions:
            return

        self.validator.validate_dissociation(incall, extension)
        self.extension_dao.dissociate_incall(incall, extension)
        self.notifier.dissociated(incall, extension)


def build_service():
    return IncallExtensionService(extension_dao,
                                  build_notifier(),
                                  build_validator())
