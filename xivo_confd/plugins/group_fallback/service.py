# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.helpers.db_manager import Session

from .notifier import build_notifier
from .validator import build_validator

import logging
logger = logging.getLogger(__name__)


class GroupFallbackService(object):

    def __init__(self, notifier, validator):
        self.validator = validator
        self.notifier = notifier

    def edit(self, group, fallbacks):
        with Session.no_autoflush:
            self.validator.validate_edit(group)
        group.fallbacks = fallbacks
        self.notifier.edited(group)


def build_service():
    return GroupFallbackService(build_notifier(),
                                build_validator())
