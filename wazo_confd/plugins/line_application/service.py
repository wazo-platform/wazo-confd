# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.line import dao as line_dao_module

from .notifier import build_notifier
from .validator import build_validator


class LineDeviceService:
    def __init__(self, validator, line_dao, notifier):
        self.validator = validator
        self.line_dao = line_dao
        self.notifier = notifier

    def associate(self, line, application):
        if line.application_uuid == application.uuid:
            return

        self.validator.validate_association(line, application)
        self.line_dao.associate_application(line, application)
        self.notifier.associated(line, application)

    def dissociate(self, line, application):
        if line.application_uuid != application.uuid:
            return

        self.validator.validate_dissociation(line, application)
        self.line_dao.dissociate_application(line, application)
        self.notifier.dissociated(line, application)


def build_service():
    validator = build_validator()
    notifier = build_notifier()
    return LineDeviceService(validator, line_dao_module, notifier)
