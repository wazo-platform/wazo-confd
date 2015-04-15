# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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

from flask import url_for

from xivo_dao.data_handler.line_extension import services as line_extension_services
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line_extension.model import LineExtension

from xivo_confd.helpers.resource import SingleAssociationResource, CollectionAssociationResource, DecoratorChain, build_response

from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int


class SingleLineExtensionResource(SingleAssociationResource):

    def get_by_extension(self, extension_id):
        association = self.service.get_by_extension_id(extension_id)
        response = self.converter.encode(association)
        location = url_for('.get_by_extension', extension_id=extension_id)
        return build_response(response, location=location)


class LineExtensionService(object):

    def __init__(self, service, line_dao, extension_dao):
        self.service = service
        self.line_dao = line_dao
        self.extension_dao = extension_dao

    def check_line_exists(self, line_id):
        self.line_dao.get(line_id)

    def check_extension_exists(self, extension_id):
        self.extension_dao.get(extension_id)

    def list(self, line_id):
        self.check_line_exists(line_id)
        return self.service.get_all_by_line_id(line_id)

    def get(self, line_id, extension_id):
        return LineExtension(line_id=line_id, extension_id=extension_id)

    def associate(self, line_extension):
        self.check_line_exists(line_extension.line_id)
        self.check_extension_exists(line_extension.extension_id)
        return self.service.associate(line_extension)

    def dissociate(self, line_extension):
        self.check_line_exists(line_extension.line_id)
        self.check_extension_exists(line_extension.extension_id)
        self.service.dissociate(line_extension)

    def get_by_parent(self, line_id):
        self.check_line_exists(line_id)
        return self.service.get_by_line_id(line_id)

    def get_by_extension_id(self, extension_id):
        self.check_extension_exists(extension_id)
        return self.service.get_by_extension_id(extension_id)


def load(core_rest_api):
    line_blueprint = core_rest_api.blueprint('lines')
    extension_blueprint = core_rest_api.blueprint('extensions')

    document = core_rest_api.content_parser.document(
        Field('line_id', Int()),
        Field('extension_id', Int())
    )
    converter = Converter.association(document, LineExtension,
                                      links={'lines': 'line_id',
                                             'extensions': 'extension_id'},
                                      rename={'parent_id': 'line_id'})

    service = LineExtensionService(line_extension_services, line_dao, extension_dao)
    single_resource = SingleLineExtensionResource(service, converter)
    collection_resource = CollectionAssociationResource(service, converter)

    chain = DecoratorChain(core_rest_api, line_blueprint)

    (chain
     .get('/<int:parent_id>/extensions')
     .decorate(collection_resource.list_association))

    (chain
     .create('/<int:parent_id>/extensions')
     .decorate(collection_resource.associate_collection))

    (chain
     .delete('/<int:parent_id>/extensions/<int:resource_id>')
     .decorate(collection_resource.dissociate_collection))

    (chain
     .get('/<int:parent_id>/extension')
     .decorate(single_resource.get_association))

    (chain
     .create('/<int:parent_id>/extension')
     .decorate(single_resource.associate))

    (chain
     .delete('/<int:parent_id>/extension')
     .decorate(single_resource.dissociate))

    (DecoratorChain(core_rest_api, extension_blueprint)
     .get('/<int:extension_id>/line')
     .decorate(single_resource.get_by_extension))

    core_rest_api.register(line_blueprint)
    core_rest_api.register(extension_blueprint)
