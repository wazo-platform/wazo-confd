# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
from dataclasses import dataclass

import phonenumbers
from xivo.caller_id import parse_caller_id
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import InputError
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.phone_number import dao as phone_number_dao
from xivo_dao.resources.user import dao as user_dao

from .notifier import build_notifier_default
from .types import CallerIDType

# Magic values stored in `userfeatures.outcallerid`, understood by wazo-agid.
DEFAULT_TOKEN = 'default'
ANONYMOUS_TOKEN = 'anonymous'

# a caller ID name is allowed 256 characters and a number 128, either of which
# alone can overflow the column the composed value is stored in
OUTGOING_CALLER_ID_MAX_LENGTH = UserFeatures.outcallerid.type.length

# an incall extension may be an Asterisk pattern, which starts with `_`
EXTEN_PATTERN_PREFIX = '_'
CALLER_ID_NUMBER_REGEX = re.compile(r'^\+?[0-9*#]+$')


@dataclass(frozen=True)
class CallerID:
    type: CallerIDType
    number: str = ''
    caller_id_name: str = ''


CallerIDAnonymous = CallerID(type='anonymous')
CallerIDDialplan = CallerID(type='default')


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


def format_caller_id(number: str, caller_id_name: str = '') -> str:
    '''
    render the value stored in `userfeatures.outcallerid`, dropping the name when
    the pair would not fit the column
    '''
    if caller_id_name:
        # `"` would break the `"Name" <number>` form the dialplan parses back out
        sanitized = caller_id_name.replace('"', '')
        formatted = f'"{sanitized}" <{number}>'
        if len(formatted) <= OUTGOING_CALLER_ID_MAX_LENGTH:
            return formatted
    return number


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


class UserCallerIDDefaultService:
    '''
    the caller ID a user presents when nothing overrides it for that call

    Applications override per call with the `X-Wazo-Selected-Caller-ID` SIP
    header. A desk phone cannot, so it presents this stored value.
    '''

    def __init__(self, callerid_service, user_dao, notifier):
        self.callerid_service = callerid_service
        self.user_dao = user_dao
        self.notifier = notifier

    def get(self, user) -> CallerID:
        stored = user.outgoing_caller_id
        # never set behaves as `default` in wazo-agid
        if not stored or stored == DEFAULT_TOKEN:
            return CallerIDDialplan
        if stored == ANONYMOUS_TOKEN:
            return CallerIDAnonymous

        # validated when written, so wazo-agid's parser accepts it
        name, number = parse_caller_id(stored) or (stored, None)
        # a number without a name parses with an empty or None name
        name = name or ''
        if number is None:
            return CallerID(type='custom', caller_id_name=name)

        # the name is configured on the phone number, not the stored value
        if available := self._find_available(user, number):
            return CallerID(
                type=available.type,
                number=number,
                caller_id_name=available.caller_id_name,
            )
        # removed from the tenant since, or set through the user API
        return CallerID(type='custom', number=number, caller_id_name=name)

    def edit(self, user, caller_id: CallerID) -> CallerID:
        if caller_id.type == 'default':
            resolved = CallerIDDialplan
            user.outgoing_caller_id = DEFAULT_TOKEN
        elif caller_id.type == 'anonymous':
            resolved = CallerIDAnonymous
            user.outgoing_caller_id = ANONYMOUS_TOKEN
        else:
            resolved = self._resolve(user, caller_id.number)
            formatted = format_caller_id(resolved.number, resolved.caller_id_name)
            # not a check of the caller ID itself: a phone number may be longer
            # than the column it is stored in
            if len(formatted) > OUTGOING_CALLER_ID_MAX_LENGTH:
                raise InputError(
                    'number is too long to be used as a caller ID, maximum is '
                    f'{OUTGOING_CALLER_ID_MAX_LENGTH} characters'
                )
            user.outgoing_caller_id = formatted

        self.user_dao.edit(user)
        self.notifier.edited(user)
        return resolved

    def _resolve(self, user, number: str) -> CallerID:
        '''
        accept a number only when the user may already present it, so an end
        user cannot assert an arbitrary caller ID. The number is stored as
        listed: wazo-agid formats it for the trunk when placing the call.
        '''
        available = self._available(user)
        if match := self._match(available, number):
            return match

        raise errors.invalid_choice('number', [c.number for c in available])

    def _find_available(self, user, number: str) -> CallerID | None:
        return self._match(self._available(user), number)

    def _available(self, user) -> list[CallerID]:
        _, callerids = self.callerid_service.search(user.id, user.tenant_uuid, {})
        # `anonymous` carries no number, it is selected by type instead
        return [callerid for callerid in callerids if callerid.type != 'anonymous']

    @staticmethod
    def _match(available, number: str) -> CallerID | None:
        if not number:
            return None
        for callerid in available:
            if same_phone_number(callerid.number, number):
                return callerid
        return None


def build_service():
    return UserCallerIDService(user_dao, incall_dao, phone_number_dao)


def build_service_default():
    return UserCallerIDDefaultService(
        build_service(), user_dao, build_notifier_default()
    )
