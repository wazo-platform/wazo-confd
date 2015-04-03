# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from flask import Blueprint
from xivo_dao.data_handler.extension import dao, validator, notifier
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.line_extension import dao as line_extension_dao

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int, Unicode, Boolean

from xivo_confd.helpers.resource import CRUDResource, CRUDService, DecoratorChain


class ExtensionService(CRUDService):

    def __init__(self, dao, line_extension_dao, line_dao,
                 validator, notifier, extra_parameters=None):
        super(ExtensionService, self).__init__(dao, validator, notifier, extra_parameters)
        self.line_extension_dao = line_extension_dao
        self.line_dao = line_dao

    def edit(self, extension):
        self.validator.validate_edit(extension)
        self.dao.edit(extension)
        self.update_line(extension)
        self.notifier.edited(extension)

    def update_line(self, extension):
        line_extension = self.line_extension_dao.find_by_extension_id(extension.id)
        if line_extension:
            self.line_dao.associate_extension(extension, line_extension.line_id)


def load(core_rest_api):
    blueprint = Blueprint('extensions',
                          __name__,
                          url_prefix='/%s/extensions' % config.API_VERSION)

    document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('exten', Unicode()),
        Field('context', Unicode()),
        Field('commented', Boolean())
    )
    converter = Converter.for_resource(document, Extension)

    service = ExtensionService(dao, line_extension_dao, line_dao, validator, notifier, ['type'])
    resource = CRUDResource(service, converter)

    DecoratorChain.register_scrud(core_rest_api, blueprint, resource)
