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

import logging

from marshmallow import ValidationError
from xivo_dao.helpers.exception import ServiceError

logger = logging.getLogger(__name__)


class ImportService(object):

    def __init__(self, entry_creator, entry_associator, entry_updater):
        self.entry_creator = entry_creator
        self.entry_associator = entry_associator
        self.entry_updater = entry_updater

    def import_rows(self, parser):
        created = []
        errors = []

        for row in parser:
            try:
                entry = self.create_entry(row)
                created.append(entry)
            except (ServiceError, ValidationError) as e:
                logger.warn("Error importing CSV row %s: %s", row.position, e)
                errors.append(row.format_error(e))

        return created, errors

    def create_entry(self, row):
        entry = self.entry_creator.create(row)
        self.entry_associator.associate(entry)
        return entry

    def update_rows(self, parser):
        updated = []
        errors = []

        for row in parser:
            try:
                entry = self.update_row(row)
                updated.append(entry)
            except (ServiceError, ValidationError) as e:
                logger.warn("ERROR importing CSV row %s: %s", row.position, e)
                errors.append(row.format_error(e))

        return updated, errors

    def update_row(self, row):
        entry = self.entry_updater.update_row(row)
        return entry
