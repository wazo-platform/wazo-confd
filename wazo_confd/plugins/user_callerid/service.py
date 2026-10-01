# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, replace

import phonenumbers
from xivo.caller_id import parse_caller_id as xivo_parse_caller_id
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import InputError
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.phone_number import dao as phone_number_dao
from xivo_dao.resources.tenant import dao as tenant_dao
from xivo_dao.resources.user import dao as user_dao

from .notifier import build_notifier_default
from .types import CallerIDDefaultType, CallerIDType

# Magic values stored in `userfeatures.outcallerid`, understood by wazo-agid.
DEFAULT_TOKEN = 'default'
ANONYMOUS_TOKEN = 'anonymous'

# a caller ID name is allowed 256 characters and a number 128, either of which
# alone can overflow the column the composed value is stored in
OUTGOING_CALLER_ID_MAX_LENGTH = UserFeatures.outcallerid.type.length


@dataclass(frozen=True)
class CallerID:
    type: CallerIDType
    number: str = ''
    caller_id_name: str = ''


@dataclass(frozen=True)
class CallerIDDefault:
    type: CallerIDDefaultType
    number: str = ''
    caller_id_name: str = ''


CallerIDAnonymous = CallerID(type='anonymous')
CallerIDDefaultAnonymous = CallerIDDefault(type='anonymous')
CallerIDDefaultDialplan = CallerIDDefault(type='default')
CallerIDDefaultUnset = CallerIDDefault(type='unset')


def same_phone_number(number1: str, number2: str) -> bool:
    '''
    compare two strings semantically as phone numbers
    '''
    result = phonenumbers.is_number_match(number1, number2)
    return result in (
        phonenumbers.MatchType.EXACT_MATCH,
        phonenumbers.MatchType.NSN_MATCH,
    )


def normalize_e164(number: str, country: str | None) -> str:
    '''
    best effort conversion to +E.164, returning the number unchanged when it
    cannot be parsed, as wazo-agid formats it per trunk anyway
    '''
    try:
        parsed = phonenumbers.parse(number, country)
    except phonenumbers.NumberParseException:
        return number
    if not phonenumbers.is_valid_number(parsed):
        return number
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


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


def parse_caller_id(stored: str) -> tuple[str, str] | None:
    '''
    inverse of `format_caller_id`, returning (number, caller_id_name), or None
    when wazo-agid could not parse the value when placing the call
    '''
    parsed = xivo_parse_caller_id(stored)
    if not parsed:
        return None

    name, number = parsed
    if number is None:
        return '', name
    if number == name and '<' not in stored:
        # a bare number, which the parser reports as both name and number
        return number, ''
    return number, name


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
            CallerID(type='associated', number=callerid.number)
            for callerid in self.user_dao.list_outgoing_callerid_associated(user_id)
            if not any(same_phone_number(callerid.number, c.number) for c in callerids)
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

    def __init__(self, callerid_service, user_dao, tenant_dao, notifier):
        self.callerid_service = callerid_service
        self.user_dao = user_dao
        self.tenant_dao = tenant_dao
        self.notifier = notifier

    def get(self, user) -> CallerIDDefault:
        stored = user.outgoing_caller_id
        if not stored:
            return CallerIDDefaultUnset
        if stored == DEFAULT_TOKEN:
            return CallerIDDefaultDialplan
        if stored == ANONYMOUS_TOKEN:
            return CallerIDDefaultAnonymous

        if not (parsed := parse_caller_id(stored)):
            # stored before outgoing_caller_id was validated
            return CallerIDDefault(type='custom', number=stored)

        number, caller_id_name = parsed
        if available := self._find_available(user, number):
            return CallerIDDefault(
                type=available.type,
                number=number,
                caller_id_name=caller_id_name or available.caller_id_name,
            )
        # removed from the tenant since, or set through the user API
        return CallerIDDefault(
            type='custom', number=number, caller_id_name=caller_id_name
        )

    def edit(self, user, caller_id_default: CallerIDDefault) -> CallerIDDefault:
        if caller_id_default.type == 'default':
            resolved = CallerIDDefaultDialplan
            user.outgoing_caller_id = DEFAULT_TOKEN
        elif caller_id_default.type == 'anonymous':
            resolved = CallerIDDefaultAnonymous
            user.outgoing_caller_id = ANONYMOUS_TOKEN
        else:
            resolved = self._resolve(user, caller_id_default.number)
            user.outgoing_caller_id = format_caller_id(
                resolved.number, resolved.caller_id_name
            )

        self.user_dao.edit(user)
        self.notifier.edited(user)
        return resolved

    def _resolve(self, user, number: str) -> CallerIDDefault:
        '''
        accept a number only when the user may already present it, so an end
        user cannot assert an arbitrary caller ID
        '''
        available = self._available(user)
        if match := self._match(available, number):
            country = self._tenant_country(user.tenant_uuid)
            resolved = replace(match, number=normalize_e164(match.number, country))
            if len(resolved.number) > OUTGOING_CALLER_ID_MAX_LENGTH:
                raise InputError(
                    'number is too long to be used as a caller ID, maximum is '
                    f'{OUTGOING_CALLER_ID_MAX_LENGTH} characters'
                )
            return resolved

        raise errors.invalid_choice('number', [c.number for c in available])

    def _find_available(self, user, number: str) -> CallerIDDefault | None:
        return self._match(self._available(user), number)

    def _available(self, user) -> list[CallerIDDefault]:
        _, callerids = self.callerid_service.search(user.id, user.tenant_uuid, {})
        return [
            CallerIDDefault(
                type=callerid.type,
                number=callerid.number,
                caller_id_name=callerid.caller_id_name,
            )
            for callerid in callerids
            # `anonymous` carries no number, it is selected by type instead
            if callerid.type != 'anonymous'
        ]

    @staticmethod
    def _match(available, number: str) -> CallerIDDefault | None:
        if not number:
            return None
        for callerid in available:
            if same_phone_number(callerid.number, number):
                return callerid
        return None

    def _tenant_country(self, tenant_uuid) -> str | None:
        tenant = self.tenant_dao.find(tenant_uuid)
        return tenant.country if tenant else None


def build_service():
    return UserCallerIDService(user_dao, incall_dao, phone_number_dao)


def build_service_default():
    return UserCallerIDDefaultService(
        build_service(), user_dao, tenant_dao, build_notifier_default()
    )
