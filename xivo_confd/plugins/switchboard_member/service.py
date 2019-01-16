# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .notifier import build_notifier
from .validator import build_validator


class SwitchboardMemberUserService(object):

    def __init__(self, notifier, validator):
        self.validator = validator
        self.notifier = notifier

    def associate_all_member_users(self, switchboard, users):
        self.validator.validate_association(switchboard, users)

        switchboard.user_members = set(users)

        self.notifier.members_associated(switchboard, users)


def build_service():
    return SwitchboardMemberUserService(build_notifier(),
                                        build_validator())
