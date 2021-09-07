# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.meeting import Meeting

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource

from .schema import MeetingSchema


class MeetingList(ListResource):

    model = Meeting
    schema = MeetingSchema

    def __init__(self, service, hostname, port):
        super().__init__(service)
        self._schema = MeetingSchema()
        self._schema.context = {'hostname': hostname, 'port': port}

    def build_headers(self, meeting):
        return {'Location': url_for('meetings', uuid=meeting.uuid, _external=True)}

    @required_acl('confd.meetings.create')
    def post(self):
        return super().post()

    @required_acl('confd.meetings.read')
    def get(self):
        return super().get()

    def schema(self):
        return self._schema


class MeetingItem(ItemResource):
    has_tenant_uuid = True

    def __init__(self, service, hostname, port):
        super().__init__(service)
        self._schema = MeetingSchema()
        self._schema.context = {'hostname': hostname, 'port': port}

    @required_acl('confd.meetings.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.meetings.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('confd.meetings.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)

    def schema(self):
        return self._schema


class GuestMeetingItem(ItemResource):
    def __init__(self, service, hostname, port):
        super().__init__(service)
        self._schema = MeetingSchema()
        # TODO(pc-m): The hostname and port are going to becore multi-tenant
        self._schema.context = {'hostname': hostname, 'port': port}

    def get(self, uuid):
        return super().get(uuid)

    def schema(self):
        return self._schema
