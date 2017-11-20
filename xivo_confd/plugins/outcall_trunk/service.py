# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from .notifier import build_notifier
from .validator import build_validator


class OutcallTrunkService(object):

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
