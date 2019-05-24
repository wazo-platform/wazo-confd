# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session

from .notifier import build_notifier
from .validator import build_validator


class GroupFallbackService:

    def __init__(self, notifier, validator):
        self.validator = validator
        self.notifier = notifier

    def edit(self, group, fallbacks):
        with Session.no_autoflush:
            self.validator.validate_edit(fallbacks)
        group.fallbacks = fallbacks
        self.notifier.edited(group)


def build_service():
    return GroupFallbackService(build_notifier(),
                                build_validator())
