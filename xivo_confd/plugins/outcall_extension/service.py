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


class OutcallExtensionService(object):

    def __init__(self, notifier, validator):
        self.notifier = notifier
        self.validator = validator

    def associate(self, outcall, extension, outcall_extension):
        if extension in outcall.extensions:
            outcall.update_extension_association(extension, **outcall_extension)
            return

        self.validator.validate_association(outcall, extension)
        outcall.associate_extension(extension, **outcall_extension)
        self.notifier.associated(outcall, extension)

    def dissociate(self, outcall, extension):
        self.validator.validate_dissociation(outcall, extension)
        outcall.dissociate_extension(extension)
        self.notifier.dissociated(outcall, extension)


def build_service():
    return OutcallExtensionService(build_notifier(),
                                   build_validator())
