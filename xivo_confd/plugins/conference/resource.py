# -*- coding: utf-8 -*-

# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
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

from flask import url_for

from xivo_dao.alchemy.conference import Conference

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import ConferenceSchema


class ConferenceList(ListResource):

    model = Conference
    schema = ConferenceSchema

    def build_headers(self, conference):
        return {'Location': url_for('conferences', id=conference.id, _external=True)}

    @required_acl('confd.conferences.create')
    def post(self):
        return super(ConferenceList, self).post()

    @required_acl('confd.conferences.read')
    def get(self):
        return super(ConferenceList, self).get()


class ConferenceItem(ItemResource):

    schema = ConferenceSchema

    @required_acl('confd.conferences.{id}.read')
    def get(self, id):
        return super(ConferenceItem, self).get(id)

    @required_acl('confd.conferences.{id}.update')
    def put(self, id):
        return super(ConferenceItem, self).put(id)

    @required_acl('confd.conferences.{id}.delete')
    def delete(self, id):
        return super(ConferenceItem, self).delete(id)
