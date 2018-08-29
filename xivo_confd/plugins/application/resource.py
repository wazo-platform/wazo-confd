# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for

from xivo_dao.alchemy.application import Application

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import ApplicationSchema


class ApplicationList(ListResource):

    # TODO multi-tenant
    model = Application
    schema = ApplicationSchema

    def build_headers(self, application):
        return {'Location': url_for('applications', application_uuid=application.uuid, _external=True)}

    @required_acl('confd.applications.create')
    def post(self):
        return super(ApplicationList, self).post()

    @required_acl('confd.applications.read')
    def get(self):
        return super(ApplicationList, self).get()


class ApplicationItem(ItemResource):

    schema = ApplicationSchema

    @required_acl('confd.applications.{application_uuid}.read')
    def get(self, application_uuid):
        return super(ApplicationItem, self).get(application_uuid)

    @required_acl('confd.applications.{application_uuid}.update')
    def put(self, application_uuid):
        return super(ApplicationItem, self).put(application_uuid)

    @required_acl('confd.applications.{application_uuid}.delete')
    def delete(self, application_uuid):
        return super(ApplicationItem, self).delete(application_uuid)
