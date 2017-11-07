# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from .notifier import build_notifier
from .validator import build_validator

from xivo_dao.resources.extension import dao as extension_dao


class GroupExtensionService(object):

    def __init__(self, extension_dao, notifier, validator):
        self.extension_dao = extension_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, group, extension):
        self.validator.validate_association(group, extension)
        self.extension_dao.associate_group(group, extension)
        self.notifier.associated(group, extension)

    def dissociate(self, group, extension):
        self.validator.validate_dissociation(group, extension)
        self.extension_dao.dissociate_group(group, extension)
        self.notifier.dissociated(group, extension)


def build_service():
    return GroupExtensionService(extension_dao,
                                 build_notifier(),
                                 build_validator())
