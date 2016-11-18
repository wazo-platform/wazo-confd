# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from flask import url_for

from xivo_dao.alchemy.voicemail import Voicemail

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import VoicemailSchema


class VoicemailList(ListResource):

    model = Voicemail
    schema = VoicemailSchema

    def build_headers(self, voicemail):
        return {'Location': url_for('voicemails', id=voicemail.id, _external=True)}

    @required_acl('confd.voicemails.create')
    def post(self):
        return super(VoicemailList, self).post()

    @required_acl('confd.voicemails.read')
    def get(self):
        return super(VoicemailList, self).get()


class VoicemailItem(ItemResource):

    schema = VoicemailSchema

    @required_acl('confd.voicemails.{id}.read')
    def get(self, id):
        return super(VoicemailItem, self).get(id)

    @required_acl('confd.voicemails.{id}.update')
    def put(self, id):
        return super(VoicemailItem, self).put(id)

    @required_acl('confd.voicemails.{id}.delete')
    def delete(self, id):
        return super(VoicemailItem, self).delete(id)
