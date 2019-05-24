# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .notifier import build_notifier
from .validator import build_validator


class OutcallTrunkService:

    def __init__(self, notifier, validator):
        self.notifier = notifier
        self.validator = validator

    def associate_all_trunks(self, outcall, trunks):
        self.validator.validate_association(outcall, trunks)
        outcall.trunks = trunks
        self.notifier.associated_all_trunks(outcall, trunks)


def build_service():
    return OutcallTrunkService(build_notifier(),
                               build_validator())
