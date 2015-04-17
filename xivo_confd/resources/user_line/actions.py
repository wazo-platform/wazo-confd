# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.data_handler.user_line import services as user_line_services
from xivo_dao.data_handler.user_line.model import UserLine
from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.line import dao as line_dao

from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int, Boolean

from xivo_confd.helpers.resource import CollectionAssociationResource, DecoratorChain


class UserLineService(object):

    def __init__(self, service, user_dao, line_dao):
        self.service = service
        self.user_dao = user_dao
        self.line_dao = line_dao

    def check_user_exists(self, user_id):
        self.user_dao.get(user_id)

    def check_line_exists(self, line_id):
        self.line_dao.get(line_id)

    def list(self, user_id):
        self.check_user_exists(user_id)
        return self.service.find_all_by_user_id(user_id)

    def get(self, user_id, line_id):
        return self.service.get_by_user_id_and_line_id(user_id, line_id)

    def associate(self, association):
        self.check_user_exists(association.user_id)
        self.check_line_exists(association.line_id)
        return self.service.associate(association)

    def dissociate(self, association):
        self.check_user_exists(association.user_id)
        self.check_line_exists(association.line_id)
        return self.service.dissociate(association)


def load(core_rest_api):
    user_blueprint = core_rest_api.blueprint('users')
    document = core_rest_api.content_parser.document(
        Field('user_id', Int()),
        Field('line_id', Int()),
        Field('main_user', Boolean()),
        Field('main_line', Boolean())
    )
    converter = Converter.association(document, UserLine,
                                      links={'users': 'user_id',
                                             'lines': 'line_id'},
                                      rename={'parent_id': 'user_id'})

    service = UserLineService(user_line_services, user_dao, line_dao)
    resource = CollectionAssociationResource(service, converter)

    chain = DecoratorChain(core_rest_api, user_blueprint)

    (chain
     .get('/<int:parent_id>/lines')
     .decorate(resource.list_association))

    (chain
     .create('/<int:parent_id>/lines')
     .decorate(resource.associate_collection))

    (chain
     .delete('/<int:parent_id>/lines/<int:resource_id>')
     .decorate(resource.dissociate_collection))

    core_rest_api.register(user_blueprint)
