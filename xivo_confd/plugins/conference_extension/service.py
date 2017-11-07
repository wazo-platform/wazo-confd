# -*- coding: UTF-8 -*-

# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.extension import dao as extension_dao

from .notifier import build_notifier
from .validator import build_validator


class ConferenceExtensionService(object):

    def __init__(self, extension_dao, notifier, validator):
        self.extension_dao = extension_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, conference, extension):
        self.validator.validate_association(conference, extension)
        self.extension_dao.associate_conference(conference, extension)
        self.notifier.associated(conference, extension)

    def dissociate(self, conference, extension):
        self.validator.validate_dissociation(conference, extension)
        self.extension_dao.dissociate_conference(conference, extension)
        self.notifier.dissociated(conference, extension)


def build_service():
    return ConferenceExtensionService(extension_dao,
                                      build_notifier(),
                                      build_validator())
