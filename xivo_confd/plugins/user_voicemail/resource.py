# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers import errors

from flask import url_for
from flask_restful import reqparse, fields, marshal

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import FieldList, Link, ConfdResource


fields = {
    'user_id': fields.Integer,
    'voicemail_id': fields.Integer,
    'links': FieldList(Link('voicemails',
                            route='voicemails.get',
                            field='voicemail_id',
                            target='resource_id'),
                       Link('users',
                            field='user_id',
                            target='id'))
}

parser = reqparse.RequestParser()
parser.add_argument('voicemail_id', type=int, required=True)


class UserVoicemailResource(ConfdResource):

    def __init__(self, service, user_dao, voicemail_dao):
        super(ConfdResource, self).__init__()
        self.service = service
        self.user_dao = user_dao
        self.voicemail_dao = voicemail_dao

    def get_voicemail_or_fail(self):
        form = parser.parse_args()
        try:
            return self.voicemail_dao.get(form['voicemail_id'])
        except NotFoundError:
            raise errors.param_not_found('voicemail_id', 'Voicemail')

    def get_user(self, user_id):
        if isinstance(user_id, int):
            return self.user_dao.get(user_id)
        return self.user_dao.get_by(uuid=str(user_id))


class UserVoicemailRoot(UserVoicemailResource):

    @required_acl('confd.users.{user_id}.voicemail.read')
    def get(self, user_id):
        user = self.get_user(user_id)
        user_voicemail = self.service.get_by(user_id=user.id)
        return marshal(user_voicemail, fields)

    @required_acl('confd.users.{user_id}.voicemail.create')
    def post(self, user_id):
        user = self.get_user(user_id)
        voicemail = self.get_voicemail_or_fail()
        user_voicemail = self.service.associate(user, voicemail)
        return marshal(user_voicemail, fields), 201, self.build_headers(user_voicemail)

    @required_acl('confd.users.{user_id}.voicemail.delete')
    def delete(self, user_id):
        user = self.get_user(user_id)
        user_voicemail = self.service.get_by(user_id=user.id)
        voicemail = self.voicemail_dao.get(user_voicemail.voicemail_id)
        self.service.dissociate(user, voicemail)
        return '', 204

    def build_headers(self, model):
        url = url_for('user_voicemails',
                      user_id=model.user_id,
                      voicemail_id=model.voicemail_id,
                      _external=True)
        return {'Location': url}


class VoicemailUserList(UserVoicemailResource):

    @required_acl('confd.voicemail.{voicemail_id}.users.read')
    def get(self, voicemail_id):
        voicemail = self.voicemail_dao.get(voicemail_id)
        items = self.service.find_all_by(voicemail_id=voicemail.id)
        return {'total': len(items),
                'items': [marshal(item, fields) for item in items]}
