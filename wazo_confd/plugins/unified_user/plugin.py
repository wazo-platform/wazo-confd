# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from .resource import UnifiedUserList
from ..user.service import build_service as build_user_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        user_service = build_user_service(provd_client)

        api.add_resource(
            UnifiedUserList,
            '/unified_users',
            endpoint='unified_users_list',
            resource_class_args=(user_service,)
        )
