# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.application import dao as application_dao
from xivo_dao.resources.line import dao as line_dao

from .resource import LineApplicationAssociation
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()
        api.add_resource(
            LineApplicationAssociation,
            '/lines/<int:line_id>/applications/<uuid:application_uuid>',
            endpoint='line_applications',
            resource_class_args=(line_dao, application_dao, service),
        )
