# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session

from .notifier import build_notifier
from .validator import build_validator


class QueueFallbackService:
    def __init__(self, notifier, validator):
        self.validator = validator
        self.notifier = notifier

    def edit(self, queue, fallbacks):
        with Session.no_autoflush:
            self.validator.validate_edit(fallbacks)
        queue.fallbacks = fallbacks
        self.notifier.edited(queue)


def build_service():
    return QueueFallbackService(build_notifier(), build_validator())
