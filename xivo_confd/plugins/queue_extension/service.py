# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.extension import dao as extension_dao_module

from .notifier import build_notifier
from .validator import build_validator


class QueueExtensionService:

    def __init__(self, extension_dao, notifier, validator):
        self.extension_dao = extension_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, queue, extension):
        if extension in queue.extensions:
            return

        self.validator.validate_association(queue, extension)
        self.extension_dao.associate_queue(queue, extension)
        self.notifier.associated(queue, extension)

    def dissociate(self, queue, extension):
        if extension not in queue.extensions:
            return

        self.validator.validate_dissociation(queue, extension)
        self.extension_dao.dissociate_queue(queue, extension)
        self.notifier.dissociated(queue, extension)


def build_service():
    return QueueExtensionService(extension_dao_module,
                                 build_notifier(),
                                 build_validator())
