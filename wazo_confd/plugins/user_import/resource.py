# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo.tenant_flask_helpers import Tenant
from xivo_dao.helpers.db_manager import Session

from wazo_confd import sysconfd, bus
from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource
from wazo_confd.representations.csv_ import output_csv

from . import csvparse
from .auth_client import auth_client


class UserImportResource(ConfdResource):
    def __init__(self, service):
        self.service = service

    @required_acl('confd.users.import.create')
    def post(self):
        tenant = Tenant.autodetect()

        parser = csvparse.parse()
        entries, errors = self.service.import_rows(parser, tenant.uuid)

        if errors:
            status_code = 400
            response = {'errors': errors}
            self.rollback()
        else:
            status_code = 201
            response = {'created': [entry.extract_ids() for entry in entries]}

        return response, status_code

    @required_acl('confd.users.import.update')
    def put_disabled(self):
        parser = csvparse.parse()
        tenant = Tenant.autodetect()
        entries, errors = self.service.update_rows(parser, tenant.uuid)

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
        auth_client.rollback()


class UserExportResource(ConfdResource):
    representations = {'text/csv; charset=utf-8': output_csv}

    def __init__(self, service):
        self.service = service

    @required_acl('confd.users.export.read')
    def get(self):
        tenant = Tenant.autodetect()
        csv_header, users = self.service.export(tenant.uuid)
        return {'headers': csv_header, 'content': users}
