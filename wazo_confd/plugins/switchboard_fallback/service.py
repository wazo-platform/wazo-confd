# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session

from .notifier import build_notifier
from .validator import build_validator


class SwitchboardFallbackService:
    def __init__(self, notifier, validator):
        self.validator = validator
        self.notifier = notifier

    def edit(self, switchboard, fallbacks):
        with Session.no_autoflush:
            self.validator.validate_edit(fallbacks)
        switchboard.fallbacks = fallbacks
        self.notifier.edited(switchboard)


def build_service():
    return SwitchboardFallbackService(build_notifier(), build_validator())
