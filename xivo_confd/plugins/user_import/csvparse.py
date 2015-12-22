# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from collections import namedtuple
import time

from xivo_dao.helpers import errors
from xivo.unicode_csv import UnicodeDictReader

from flask import request


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


class CsvRow(object):

    USER_RULES = (
        UnicodeRule('uuid', 'uuid'),
        UnicodeRule('firstname', 'firstname'),
        UnicodeRule('lastname', 'lastname'),
        UnicodeRule('username', 'username'),
        UnicodeRule('password', 'password'),
        UnicodeRule('language', 'language'),
        UnicodeRule('outgoing_caller_id', 'outgoing_caller_id'),
        UnicodeRule('mobile_phone_number', 'mobile_phone_number'),
        UnicodeRule('userfield', 'userfield'),
        BooleanRule('supervision_enabled', 'supervision_enabled'),
        BooleanRule('call_transfer_enabled', 'call_transfer_enabled'),
        IntRule('entity_id', 'entity_id'),
        IntRule('ring_seconds', 'ring_seconds'),
        IntRule('simultaneous_calls', 'simultaneous_calls'),
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
        UnicodeRule('sip_username', 'name'),
        UnicodeRule('sip_secret', 'secret'),
    )

    EXTENSION_RULES = (
        UnicodeRule('exten', 'exten'),
        UnicodeRule('context', 'context'),
    )

    CTI_PROFILE_RULES = (
        UnicodeRule('cti_profile_name', 'name'),
        BooleanRule('cti_profile_enabled', 'enabled'),
    )

    INCALL_RULES = (
        UnicodeRule('incall_exten', 'exten'),
        UnicodeRule('incall_context', 'context'),
        IntRule('incall_ring_seconds', 'ring_seconds'),
    )

    def __init__(self, fields, position):
        self.fields = fields
        self.position = position

    def parse(self):
        return {
            'user': self.parse_rules(self.USER_RULES),
            'voicemail': self.parse_rules(self.VOICEMAIL_RULES),
            'line': self.parse_rules(self.LINE_RULES),
            'sip': self.parse_rules(self.SIP_RULES),
            'extension': self.parse_rules(self.EXTENSION_RULES),
            'incall': self.parse_rules(self.INCALL_RULES),
            'cti_profile': self.parse_rules(self.CTI_PROFILE_RULES),
            'extension': self.parse_rules(self.EXTENSION_RULES),
            'sccp': {},
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
