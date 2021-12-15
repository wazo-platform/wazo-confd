# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.validator import ValidationGroup, Validator
from xivo_dao.helpers import errors
from xivo_dao.resources.meeting_authorization import dao


class MeetingAuthorizationMaxQuota(Validator):
    max_quota = 128

    def validate(self, model):
        meeting_uuid = model.meeting_uuid
        existing_authorizations = dao.find_all_by(meeting_uuid)
        if len(existing_authorizations) >= self.max_quota:
            raise errors.quota_exceeded('Meeting Authorization', self.max_quota)


def build_validator():
    return ValidationGroup(create=[MeetingAuthorizationMaxQuota()])
