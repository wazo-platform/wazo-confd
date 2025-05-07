# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource
from wazo_confd.plugins.endpoint_sip.schema import (
    EndpointSIPSchema,
    GETQueryStringSchema,
    MergedEndpointSIPSchema,
)


class UserLineAssociatedEndpointSipItem(ConfdResource):
    schema = EndpointSIPSchema
    view_schemas = {
        'merged': MergedEndpointSIPSchema,
    }

    def __init__(self, user_dao, line_dao):
        super().__init__()
        self.user_dao = user_dao
        self.line_dao = line_dao

    @required_acl(
        'confd.users.{user_uuid}.lines.{line_id}.associated.endpoints.sip.read'
    )
    def get(self, user_uuid, line_id):
        user = self.user_dao.get_by(uuid=str(user_uuid))
        view = GETQueryStringSchema().load(request.args)['view']
        schema = self.view_schemas.get(view, self.schema)

        if line_id == 'main':
            if not user.lines:
                return 'Resource Not Found.', 404
            line = user.lines[0]
        else:
            line = self.line_dao.get(line_id)
            if line not in user.lines:
                return 'Resource Not Found.', 404

        if not line.endpoint_sip:
            return 'Resource Not Found.', 404

        return schema().dump(line.endpoint_sip)
