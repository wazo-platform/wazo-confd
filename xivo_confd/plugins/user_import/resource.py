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

from xivo_dao.helpers.db_manager import Session

from xivo_confd.representations.csv_ import output_csv
from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource
from xivo_confd.plugins.user_import import csvparse
from xivo_confd.database import user_export as user_export_db
from xivo_confd import sysconfd, bus


class UserImportResource(ConfdResource):

    def __init__(self, service):
        self.service = service

    @required_acl('confd.users.import.create')
    def post(self):
        parser = csvparse.parse()
        entries, errors = self.service.import_rows(parser)

        if errors:
            status_code = 400
            response = {'errors': errors}
            self.rollback()
        else:
            status_code = 201
            response = {'created': [entry.extract_ids() for entry in entries]}

        return response, status_code

    @required_acl('confd.users.import.update')
    def put(self):
        parser = csvparse.parse()
        entries, errors = self.service.update_rows(parser)

        if errors:
            status_code = 400
            response = {'errors': errors}
            self.rollback()
        else:
            status_code = 201
            response = {'updated': [entry.extract_ids() for entry in entries]}

        return response, status_code

    def rollback(self):
        Session.rollback()
        sysconfd.rollback()
        bus.rollback()


class UserExportResource(ConfdResource):

    representations = {'text/csv; charset=utf-8': output_csv}

    @required_acl('confd.users.export.read')
    def get(self):
        csv_header, users = user_export_db.export_query()
        return {
            'headers': csv_header,
            'content': list(self._format_users(csv_header, users))
        }

    def _format_users(self, header, users):
        for user in users:
            user_row = tuple((field or "") for field in user)
            user_dict = dict(zip(header, user_row))
            yield user_dict
