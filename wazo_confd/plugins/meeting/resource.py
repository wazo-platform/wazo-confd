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

    def build_headers(self, meeting):
        return {'Location': url_for('meetings', uuid=meeting.uuid, _external=True)}

    @required_acl('confd.meetings.create')
    def post(self):
        return super().post()

    @required_acl('confd.meetings.read')
    def get(self):
        return super().get()


class MeetingItem(ItemResource):
    schema = MeetingSchema
    has_tenant_uuid = True

    @required_acl('confd.meetings.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.meetings.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('confd.meetings.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)
