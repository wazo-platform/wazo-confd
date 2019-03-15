# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import time

from collections import namedtuple
from flask import request

from xivo.unicode_csv import UnicodeDictReader
from xivo_dao.helpers import errors


ParseRule = namedtuple('ParseRule', ['csv_name', 'parser', 'name'])


class CsvParser(object):

    def __init__(self, lines, encoding):
        self.reader = UnicodeDictReader(lines, encoding=encoding)

    def __iter__(self):
        return CsvIterator(self.reader)


class CsvIterator(object):

    def __init__(self, reader):
        self.reader = reader
        self.position = 0

    def next(self):
        row = next(self.reader)
        self.position += 1
        return CsvRow(row, self.position)


class Rule(object):

    def __init__(self, csv_name, name):
        self.csv_name = csv_name
        self.name = name

    def insert(self, fields, entry):
        if self.csv_name in fields:
            value = fields.get(self.csv_name, "")
            entry[self.name] = self.parse(value)


class UnicodeRule(Rule):

    def parse(self, value):
        if value == "":
            return None
        return value


class BooleanRule(Rule):

    def parse(self, value):
        if value == "":
            return None
        if value not in ("0", "1"):
            raise errors.invalid_choice(self.csv_name, ["0", "1"])
        return value == "1"


class IntRule(Rule):

    def parse(self, value):
        if value == "":
            return None
        if not value.isdigit():
            raise errors.wrong_type(self.csv_name, 'integer')
        return int(value)


class ColonListRule(Rule):

    def parse(self, value):
        if value == "":
            return []
        return value.split(";")


class CsvRow(object):

    USER_RULES = (
        UnicodeRule('uuid', 'uuid'),
        UnicodeRule('firstname', 'firstname'),
        UnicodeRule('lastname', 'lastname'),
        UnicodeRule('email', 'email'),
        UnicodeRule('language', 'language'),
        UnicodeRule('outgoing_caller_id', 'outgoing_caller_id'),
        UnicodeRule('mobile_phone_number', 'mobile_phone_number'),
        UnicodeRule('call_permission_password', 'call_permission_password'),
        UnicodeRule('userfield', 'userfield'),
        BooleanRule('enabled', 'enabled'),
        BooleanRule('supervision_enabled', 'supervision_enabled'),
        BooleanRule('call_transfer_enabled', 'call_transfer_enabled'),
        BooleanRule('dtmf_hangup_enabled', 'dtmf_hangup_enabled'),
        BooleanRule('call_record_enabled', 'call_record_enabled'),
        BooleanRule('online_call_record_enabled', 'online_call_record_enabled'),
        IntRule('ring_seconds', 'ring_seconds'),
        IntRule('simultaneous_calls', 'simultaneous_calls'),
    )

    CONTEXT_RULES = (
        UnicodeRule('context', 'context'),
    )

    ENTITY_RULES = (
        IntRule('entity_id', 'id'),
    )

    VOICEMAIL_RULES = (
        UnicodeRule('voicemail_name', 'name'),
        UnicodeRule('voicemail_number', 'number'),
        UnicodeRule('voicemail_context', 'context'),
        UnicodeRule('voicemail_password', 'password'),
        UnicodeRule('voicemail_email', 'email'),
        BooleanRule('voicemail_attach_audio', 'attach_audio'),
        BooleanRule('voicemail_delete_messages', 'delete_messages'),
        BooleanRule('voicemail_ask_password', 'ask_password'),
    )

    LINE_RULES = (
        UnicodeRule('line_protocol', 'endpoint'),
        UnicodeRule('context', 'context'),
    )

    SIP_RULES = (
        UnicodeRule('sip_username', 'username'),
        UnicodeRule('sip_secret', 'secret'),
    )

    EXTENSION_RULES = (
        UnicodeRule('exten', 'exten'),
        UnicodeRule('context', 'context'),
    )

    CTI_PROFILE_RULES = (
        UnicodeRule('cti_profile_name', 'name'),
    )

    INCALL_RULES = (
        UnicodeRule('incall_exten', 'exten'),
        UnicodeRule('incall_context', 'context'),
        IntRule('incall_ring_seconds', 'ring_seconds'),
    )

    CALL_PERMISSION_RULES = (
        ColonListRule('call_permissions', 'names'),
    )

    WAZO_USER_RULES = (
        UnicodeRule('uuid', 'uuid'),
        UnicodeRule('firstname', 'firstname'),
        UnicodeRule('lastname', 'lastname'),
        UnicodeRule('email', 'email_address'),
        UnicodeRule('username', 'username'),
        UnicodeRule('password', 'password'),
        BooleanRule('cti_profile_enabled', 'enabled'),

    )

    def __init__(self, fields, position):
        self.fields = fields
        self.position = position

    def parse(self):
        return {
            'user': self.parse_rules(self.USER_RULES),
            'wazo_user': self.parse_rules(self.WAZO_USER_RULES),
            'entity': self.parse_rules(self.ENTITY_RULES),
            'voicemail': self.parse_rules(self.VOICEMAIL_RULES),
            'line': self.parse_rules(self.LINE_RULES),
            'sip': self.parse_rules(self.SIP_RULES),
            'extension_incall': self.parse_rules(self.INCALL_RULES),
            'incall': self.parse_rules(self.INCALL_RULES),
            'cti_profile': self.parse_rules(self.CTI_PROFILE_RULES),
            'extension': self.parse_rules(self.EXTENSION_RULES),
            'call_permissions': self.parse_rules(self.CALL_PERMISSION_RULES),
            'sccp': {},
            'context': self.parse_rules(self.CONTEXT_RULES),
        }

    def parse_rules(self, rules):
        entry = {}
        for rule in rules:
            rule.insert(self.fields, entry)
        return entry

    def format_error(self, exc):
        return {'message': unicode(exc),
                'timestamp': int(time.time()),
                'details': {'row': self.fields,
                            'row_number': self.position}}


def parse():
    charset = request.mimetype_params.get('charset', 'utf-8')
    lines = request.data.split("\n")
    return CsvParser(lines, charset)
