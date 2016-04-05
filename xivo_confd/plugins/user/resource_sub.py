# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from flask_restful import reqparse, fields, marshal

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import Strict, ConfdResource


class UserSubResource(ConfdResource):

    def __init__(self, service):
        self.service = service

    def get(self, user_id):
        user = self.service.get(user_id)
        return marshal(user, self.fields)

    def put(self, user_id):
        user = self.service.get(user_id)
        self.parse_and_update(user)
        return '', 204

    def parse_and_update(self, model):
        form = self.parser.parse_args()
        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model, self.name)


class UserServiceDND(UserSubResource):

    fields = {'enabled': fields.Boolean(attribute='dnd_enabled')}
    parser = (reqparse.RequestParser()
              .add_argument('enabled', type=Strict(bool), store_missing=False, required=True, nullable=False,
                            dest='dnd_enabled'))
    name = 'dnd'

    @required_acl('confd.users.{user_id}.services.dnd.read')
    def get(self, user_id):
        return super(UserServiceDND, self).get(user_id)

    @required_acl('confd.users.{user_id}.services.dnd.update')
    def put(self, user_id):
        return super(UserServiceDND, self).put(user_id)


class UserServiceIncallFilter(UserSubResource):

    fields = {'enabled': fields.Boolean(attribute='incallfilter_enabled')}
    parser = (reqparse.RequestParser()
              .add_argument('enabled', type=Strict(bool), store_missing=False, required=True, nullable=False,
                            dest='incallfilter_enabled'))
    name = 'incallfilter'

    @required_acl('confd.users.{user_id}.services.dnd.read')
    def get(self, user_id):
        return super(UserServiceIncallFilter, self).get(user_id)

    @required_acl('confd.users.{user_id}.services.dnd.update')
    def put(self, user_id):
        return super(UserServiceIncallFilter, self).put(user_id)


class UserServiceList(UserSubResource):

    fields = {'dnd': UserServiceDND.fields,
              'incallfilter': UserServiceIncallFilter.fields}

    @required_acl('confd.users.{user_id}.services.read')
    def get(self, user_id):
        return super(UserServiceList, self).get(user_id)


class UserForwardBusy(UserSubResource):

    fields = {'enabled': fields.Boolean(attribute='busy_enabled'),
              'destination': fields.String(attribute='busy_destination')}
    parser = (reqparse.RequestParser()
              .add_argument('enabled', type=Strict(bool), store_missing=False, nullable=False,
                            dest='busy_enabled')
              .add_argument('destination', type=Strict(unicode), store_missing=False,
                            dest='busy_destination'))
    name = 'busy'

    @required_acl('confd.users.{user_id}.forwards.busy.read')
    def get(self, user_id):
        return super(UserForwardBusy, self).get(user_id)

    @required_acl('confd.users.{user_id}.forwards.busy.update')
    def put(self, user_id):
        return super(UserForwardBusy, self).put(user_id)


class UserForwardNoAnswer(UserSubResource):

    fields = {'enabled': fields.Boolean(attribute='noanswer_enabled'),
              'destination': fields.String(attribute='noanswer_destination')}
    parser = (reqparse.RequestParser()
              .add_argument('enabled', type=Strict(bool), store_missing=False, nullable=False,
                            dest='noanswer_enabled')
              .add_argument('destination', type=Strict(unicode), store_missing=False,
                            dest='noanswer_destination'))
    name = 'noanswer'

    @required_acl('confd.users.{user_id}.forwards.noanswer.read')
    def get(self, user_id):
        return super(UserForwardNoAnswer, self).get(user_id)

    @required_acl('confd.users.{user_id}.forwards.noanswer.update')
    def put(self, user_id):
        return super(UserForwardNoAnswer, self).put(user_id)


class UserForwardUnconditional(UserSubResource):

    fields = {'enabled': fields.Boolean(attribute='unconditional_enabled'),
              'destination': fields.String(attribute='unconditional_destination')}
    parser = (reqparse.RequestParser()
              .add_argument('enabled', type=Strict(bool), store_missing=False, nullable=False,
                            dest='unconditional_enabled')
              .add_argument('destination', type=Strict(unicode), store_missing=False,
                            dest='unconditional_destination'))
    name = 'unconditional'

    @required_acl('confd.users.{user_id}.forwards.unconditional.read')
    def get(self, user_id):
        return super(UserForwardUnconditional, self).get(user_id)

    @required_acl('confd.users.{user_id}.forwards.unconditional.update')
    def put(self, user_id):
        return super(UserForwardUnconditional, self).put(user_id)


class UserForwardList(UserSubResource):

    fields = {'busy': UserForwardBusy.fields,
              'noanswer': UserForwardNoAnswer.fields,
              'unconditional': UserForwardUnconditional.fields}

    @required_acl('confd.users.{user_id}.forwards.read')
    def get(self, user_id):
        return super(UserForwardList, self).get(user_id)
