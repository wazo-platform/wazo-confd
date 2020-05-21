# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.conference import Conference

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import ConferenceSchema


class ConferenceList(ListResource):

    model = Conference
    schema = ConferenceSchema

    def build_headers(self, conference):
        return {'Location': url_for('conferences', id=conference.id, _external=True)}

    @required_acl('confd.conferences.create')
    def post(self):
        return super().post()

    @required_acl('confd.conferences.read')
    def get(self):
        return super().get()


class ConferenceItem(ItemResource):

    schema = ConferenceSchema
    has_tenant_uuid = True

    @required_acl('confd.conferences.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.conferences.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.conferences.{id}.delete')
    def delete(self, id):
        return super().delete(id)
