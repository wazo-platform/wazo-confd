# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.phone_number import dao as phone_number_dao
from dataclasses import dataclass
from typing import Literal
import phonenumbers

CallerIDType = Literal['main', 'associated', 'anonymous', 'shared']


class CallerIDAnonymous:
    type = 'anonymous'


@dataclass()
class CallerID:
    type: CallerIDType
    number: str


def same_phone_number(number1: str, number2: str) -> bool:
    '''
    compare two strings semantically as phone numbers
    '''
    result = phonenumbers.is_number_match(number1, number2)
    if result == phonenumbers.MatchType.NO_MATCH:
        return False
    else:
        return True


class UserCallerIDService:
    def __init__(self, user_dao, incall_dao, phone_number_dao):
        self.user_dao = user_dao
        self.incall_dao = incall_dao
        self.phone_number_dao = phone_number_dao

    def search(self, user_id, tenant_uuid, parameters):
        callerids = []
        if main_callerid := self.phone_number_dao.find_by(
            main=True, tenant_uuids=[tenant_uuid]
        ):
            callerids.append(CallerID(type='main', number=main_callerid.number))
        shared_callerids = self.phone_number_dao.find_all_by(
            shared=True, main=False, tenant_uuids=[tenant_uuid]
        )
        callerids.extend(
            CallerID(type='shared', number=callerid.number)
            for callerid in shared_callerids
        )
        callerids.extend(
            callerid
            for callerid in self.user_dao.list_outgoing_callerid_associated(user_id)
            if not any(same_phone_number(callerid.number, c.number) for c in callerids)
        )
        callerids.append(CallerIDAnonymous)
        return len(callerids), callerids


def build_service():
    return UserCallerIDService(user_dao, incall_dao, phone_number_dao)
