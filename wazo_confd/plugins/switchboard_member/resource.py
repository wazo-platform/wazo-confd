# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request


from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class SwitchboardMemberUserItem(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, middleware):
        super().__init__()
        self._middleware = middleware

    @required_acl('confd.switchboards.{switchboard_uuid}.members.users.update')
    def put(self, switchboard_uuid):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.associate(request.get_json(), switchboard_uuid, tenant_uuids)
        return '', 204
