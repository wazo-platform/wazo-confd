# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao_module


class UserSubscription:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def list(self, tenant_uuid):
        return self.user_dao.count_all_by('subscription_type', tenant_uuid=tenant_uuid)


def build_service():
    return UserSubscription(user_dao_module)
