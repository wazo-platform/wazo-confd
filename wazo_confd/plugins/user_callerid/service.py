# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.incall import dao as incall_dao


class CallerIDAnonymous:
    type = 'anonymous'


class UserCallerIDService:
    def __init__(self, user_dao, incall_dao):
        self.user_dao = user_dao
        self.incall_dao = incall_dao

    def search(self, user_id, tenant_uuid, parameters):
        callerids = []
        if main_callerid := self.incall_dao.find_main_callerid(tenant_uuid):
            callerids.append(main_callerid)
        callerids.extend(self.user_dao.list_outgoing_callerid_associated(user_id))
        callerids.append(CallerIDAnonymous)
        return len(callerids), callerids


def build_service():
    return UserCallerIDService(user_dao, incall_dao)
