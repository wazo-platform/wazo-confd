# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from xivo_dao.resources.incall.model import Incall

from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.context import dao as context_dao

from xivo_confd.resources.user_line_extension import services as ule_services
from xivo_confd.resources.line_extension import validator as line_extension_validator
from xivo_confd.resources.line_device import validator as line_device_validator
from xivo_confd.resources.extensions import validator as extension_validator


def build_manager():
    incall = IncallAssociator(line_extension_validator, user_line_dao, incall_dao, extension_dao)
    internal = InternalAssociator(ule_services,
                                  extension_validator,
                                  line_extension_validator,
                                  line_device_validator)
    associators = {'incall': incall, 'internal': internal}
    return AssociationManager(context_dao, line_extension_validator, associators)


class AssociationManager(object):

    def __init__(self, context_dao, validator, associators):
        self.context_dao = context_dao
        self.validator = validator
        self.associators = associators

    def associate(self, line_extension):
        self.validate(line_extension)

        associator = self._get_associator(line_extension)
        associator.associate(line_extension)

    def _get_associator(self, line_extension):
        context = self.context_dao.get_by_extension_id(line_extension.extension_id)

        if context.type not in self.associators:
            raise NotImplementedError("Associator for contexts of type '%s' not implemented" % context.type)

        return self.associators[context.type]

    def validate(self, line_extension):
        self.validator.validate_model(line_extension)
        self.validator.validate_line(line_extension)
        self.validator.validate_extension(line_extension)

    def dissociate(self, line_extension):
        self.validate(line_extension)
        self.validator.validate_associated(line_extension)

        associator = self._get_associator(line_extension)
        associator.dissociate(line_extension)


class InternalAssociator(object):

    def __init__(self, ule_services, extension_validator, line_extension_validator, line_device_validator):
        self.ule_services = ule_services
        self.extension_validator = extension_validator
        self.line_extension_validator = line_extension_validator
        self.line_device_validator = line_device_validator

    def associate(self, line_extension):
        self.line_extension_validator.validate_line_not_associated_to_extension(line_extension)
        self.extension_validator.validate_extension_not_associated(line_extension.extension_id)
        self.ule_services.associate_line_extension(line_extension)

    def dissociate(self, line_extension):
        self.line_device_validator.validate_no_device(line_extension.line_id)
        self.ule_services.dissociate_line_extension(line_extension)


class IncallAssociator(object):

    def __init__(self, validator, user_line_dao, incall_dao, extension_dao):
        self.validator = validator
        self.user_line_dao = user_line_dao
        self.incall_dao = incall_dao
        self.extension_dao = extension_dao

    def associate(self, line_extension):
        self.validator.validate_associated_to_user(line_extension)
        self._create_incall(line_extension)

    def _create_incall(self, line_extension):
        main_user_line = self.user_line_dao.find_main_user_line(line_extension.line_id)
        incall = Incall.user_destination(main_user_line.user_id,
                                         line_extension.extension_id)
        created_incall = self.incall_dao.create(incall)
        self.extension_dao.associate_destination(line_extension.extension_id, 'incall', created_incall.id)

    def dissociate(self, line_extension):
        incall = self.incall_dao.find_by_extension_id(line_extension.extension_id)
        self.incall_dao.delete(incall)
        self.extension_dao.dissociate_extension(line_extension.extension_id)
