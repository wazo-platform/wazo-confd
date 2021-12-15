# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request
from wazo_confd.auth import no_auth
from wazo_confd.helpers.restful import ItemResource, ListResource
from xivo_dao.alchemy.meeting_authorization import MeetingAuthorization
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from .schema import (
    MeetingAuthorizationSchema,
    MeetingAuthorizationIDSchema,
)


class GuestMeetingAuthorizationList(ListResource):

    model = MeetingAuthorization
    schema = MeetingAuthorizationSchema

    def __init__(self, service, meeting_dao):
        self._service = service
        self._meeting_dao = meeting_dao

    def build_headers(self, meeting_authorization):
        return {
            'Location': url_for(
                'guest_meeting_authorization_list',
                guest_uuid=meeting_authorization.guest_uuid,
                meeting_uuid=meeting_authorization.meeting_uuid,
                authorization_uuid=meeting_authorization.uuid,
                _external=True,
            )
        }

    @no_auth
    def post(self, guest_uuid, meeting_uuid):
        body = request.get_json()
        body['guest_uuid'] = guest_uuid
        body['meeting_uuid'] = meeting_uuid
        form = self.schema().load(body)
        form['status'] = 'pending'

        try:
            self._meeting_dao.get(meeting_uuid)
        except NotFoundError as e:
            raise errors.not_found('meetings', 'Meeting', **e.metadata)

        model = self.model(**form)
        self._service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)


class GuestMeetingAuthorizationItem(ItemResource):
    model = MeetingAuthorization
    schema = MeetingAuthorizationIDSchema

    def __init__(self, service, meeting_dao):
        self._service = service
        self._meeting_dao = meeting_dao

    @no_auth
    def get(self, guest_uuid, meeting_uuid, authorization_uuid):
        ids = {
            'guest_uuid': guest_uuid,
            'meeting_uuid': meeting_uuid,
            'uuid': authorization_uuid,
        }
        ids = self.schema().load(ids)
        try:
            self._meeting_dao.get(ids['meeting_uuid'])
        except NotFoundError as e:
            raise errors.not_found('meetings', 'Meeting', **e.metadata)

        try:
            model = self._service.get(
                ids['guest_uuid'], ids['meeting_uuid'], ids['uuid']
            )
        except NotFoundError as e:
            raise errors.not_found(
                'meeting_authorizations', 'MeetingAuthorization', **e.metadata
            )

        return self.schema().dump(model)
