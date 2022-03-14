# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.meeting_authorization import dao

from wazo_confd.helpers.resource import CRUDService

from .validator import build_validator


class MeetingAuthorizationService(CRUDService):
    def search(self, parameters, meeting_uuid):
        return self.dao.search(meeting_uuid, **parameters)

    def get(self, guest_uuid, meeting_uuid, authorization_uuid, **kwargs):
        return self.dao.get(meeting_uuid, authorization_uuid, guest_uuid, **kwargs)

    def accept(self, meeting_authorization):
        meeting_authorization.status = 'accepted'
        return self.dao.edit(meeting_authorization)

    def reject(self, meeting_authorization):
        meeting_authorization.status = 'rejected'
        return self.dao.edit(meeting_authorization)


def build_service(notifier):
    return MeetingAuthorizationService(dao, build_validator(), notifier)
