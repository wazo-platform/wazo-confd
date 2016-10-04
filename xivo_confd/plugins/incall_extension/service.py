# -*- coding: UTF-8 -*-

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

from .notifier import build_notifier
from .validator import build_validator

from xivo_dao.resources.extension import dao as extension_dao


class IncallExtensionService(object):

    def __init__(self, extension_dao, notifier, validator):
        self.extension_dao = extension_dao
        self.validator = validator
        self.notifier = notifier

    def get(self, incall, extension):
        return self.extension_dao.get_by(type='incall', typeval=str(incall.id), id=extension.id)

    def associate(self, incall, extension):
        self.validator.validate_association(incall, extension)
        self.extension_dao.associate_incall(incall, extension)
        self.notifier.associated(incall, extension)

    def dissociate(self, incall, extension):
        self.validator.validate_dissociation(incall, extension)
        self.extension_dao.dissociate_incall(incall, extension)
        self.notifier.dissociated(incall, extension)


def build_service():
    return IncallExtensionService(extension_dao,
                                  build_notifier(),
                                  build_validator())
