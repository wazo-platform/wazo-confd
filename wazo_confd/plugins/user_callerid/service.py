# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
from dataclasses import dataclass

import phonenumbers
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.phone_number import dao as phone_number_dao
from xivo_dao.resources.user import dao as user_dao

from .types import CallerIDType

# an incall extension may be an Asterisk pattern, which starts with `_`
EXTEN_PATTERN_PREFIX = '_'
CALLER_ID_NUMBER_REGEX = re.compile(r'^\+?[0-9*#]+$')


@dataclass(frozen=True)
class CallerID:
    type: CallerIDType
    number: str = ''
    caller_id_name: str = ''


CallerIDAnonymous = CallerID(type='anonymous')


def number_from_exten(exten: str) -> str | None:
    '''
    the number an incall extension presents as a caller ID, or None when it is a
    pattern matching more than one number, such as `_555XXXX`
    '''
    number = exten.removeprefix(EXTEN_PATTERN_PREFIX)
    return number if CALLER_ID_NUMBER_REGEX.match(number) else None


def same_phone_number(number1: str, number2: str) -> bool:
    '''
    compare two strings semantically as phone numbers
    '''
    result = phonenumbers.is_number_match(number1, number2)
    return result in (
        phonenumbers.MatchType.EXACT_MATCH,
        phonenumbers.MatchType.NSN_MATCH,
    )


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
            callerids.append(
                CallerID(
                    type='main',
                    number=main_callerid.number,
                    caller_id_name=main_callerid.caller_id_name or '',
                )
            )

        # consider "associated" caller ids from incalls
        # as having precedence over shared phone numbers
        callerids.extend(
            CallerID(type='associated', number=number)
            for callerid in self.user_dao.list_outgoing_callerid_associated(user_id)
            if (number := number_from_exten(callerid.number))
            and not any(same_phone_number(number, c.number) for c in callerids)
        )
        shared_callerids = self.phone_number_dao.find_all_by(
            shared=True, main=False, tenant_uuids=[tenant_uuid]
        )
        callerids.extend(
            CallerID(
                type='shared',
                number=callerid.number,
                caller_id_name=callerid.caller_id_name or '',
            )
            for callerid in shared_callerids
            if not any(same_phone_number(callerid.number, c.number) for c in callerids)
        )
        callerids.append(CallerIDAnonymous)
        return len(callerids), callerids


def build_service():
    return UserCallerIDService(user_dao, incall_dao, phone_number_dao)
