# -*- coding: UTF-8 -*-

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

from .notifier import build_notifier
from .validator import build_validator

from xivo_dao.resources.extension import dao as extension_dao


class GroupExtensionService(object):

    def __init__(self, extension_dao, notifier, validator):
        self.extension_dao = extension_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, group, extension):
        self.validator.validate_association(group, extension)
        self.extension_dao.associate_group(group, extension)
        self.notifier.associated(group, extension)

    def dissociate(self, group, extension):
        self.validator.validate_dissociation(group, extension)
        self.extension_dao.dissociate_group(group, extension)
        self.notifier.dissociated(group, extension)


def build_service():
    return GroupExtensionService(extension_dao,
                                 build_notifier(),
                                 build_validator())
