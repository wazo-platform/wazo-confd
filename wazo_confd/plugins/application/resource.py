# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for
from xivo_dao.alchemy.application import Application

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource

from .schema import ApplicationSchema


class ApplicationList(ListResource):
    model = Application
    schema = ApplicationSchema

    def build_headers(self, application):
        return {
            'Location': url_for(
                'applications', application_uuid=application.uuid, _external=True
            )
        }

    @required_acl('confd.applications.create')
    def post(self):
        return super().post()

    @required_acl('confd.applications.read')
    def get(self):
        return super().get()


class ApplicationItem(ItemResource):
    schema = ApplicationSchema
    has_tenant_uuid = True

    @required_acl('confd.applications.{application_uuid}.read')
    def get(self, application_uuid):
        return super().get(application_uuid)

    @required_acl('confd.applications.{application_uuid}.update')
    def put(self, application_uuid):
        return super().put(application_uuid)

    @required_acl('confd.applications.{application_uuid}.delete')
    def delete(self, application_uuid):
        return super().delete(application_uuid)
