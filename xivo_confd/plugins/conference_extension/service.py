# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Francois Blackburn
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

from xivo_dao.resources.extension import dao as extension_dao

from .notifier import build_notifier
from .validator import build_validator


class ConferenceExtensionService(object):

    def __init__(self, extension_dao, notifier, validator):
        self.extension_dao = extension_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, conference, extension):
        self.validator.validate_association(conference, extension)
        self.extension_dao.associate_conference(conference, extension)
        self.notifier.associated(conference, extension)

    def dissociate(self, conference, extension):
        self.validator.validate_dissociation(conference, extension)
        self.extension_dao.dissociate_conference(conference, extension)
        self.notifier.dissociated(conference, extension)


def build_service():
    return ConferenceExtensionService(extension_dao,
                                      build_notifier(),
                                      build_validator())
