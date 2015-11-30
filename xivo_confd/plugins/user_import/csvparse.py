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

import time

from xivo_dao.helpers import errors
from xivo.unicode_csv import UnicodeDictReader

from flask import request


class CsvParser(object):

    def __init__(self, lines, encoding):
        self.reader = UnicodeDictReader(lines, encoding=encoding)

    def __iter__(self):
        return self

    def next(self):
        row = next(self.reader)
        return CsvRow(row)


class CsvRow(object):

    def __init__(self, fields):
        self.fields = fields

    def parse(self):
        parsed = {}

        if self.columns_have_values('firstname'):
            parsed['user'] = {
                'firstname': self.parse_unicode('firstname'),
                'lastname': self.parse_unicode('lastname'),
                'username': self.parse_unicode('username'),
                'password': self.parse_unicode('password'),
                'language': self.parse_unicode('language'),
                'outgoing_caller_id': self.parse_unicode('outgoing_caller_id'),
                'mobile_phone_number': self.parse_unicode('mobile_phone_number'),
                'cti_enabled': self.parse_bool('cti_enabled'),
                'supervision_enabled': self.parse_bool('supervision_enabled'),
                'call_transfer_enabled': self.parse_bool('call_transfer_enabled'),
                'entity_id': self.parse_int('entity_id'),
            }
        else:
            raise errors.missing('firstname')

        if self.columns_have_values('voicemail_name', 'voicemail_number', 'voicemail_context'):
            parsed['voicemail'] = {
                'name': self.parse_unicode('voicemail_name'),
                'number': self.parse_unicode('voicemail_number'),
                'context': self.parse_unicode('voicemail_context'),
                'password': self.parse_unicode('voicemail_password'),
                'email': self.parse_unicode('voicemail_email'),
                'attach_audio': self.parse_bool('voicemail_attach_audio'),
                'delete_messages': self.parse_bool('voicemail_delete_messages'),
                'ask_password': self.parse_bool('voicemail_ask_password'),
            }

        if self.columns_have_values('line_protocol'):
            protocol = self.fields.get('line_protocol')

            parsed['line'] = {
                'context': self.parse_unicode('context')
            }

            if protocol == 'sip':
                parsed['sip'] = {
                    'name': self.parse_unicode('sip_username'),
                    'secret': self.parse_unicode('sip_secret')
                }
            elif protocol == 'sccp':
                parsed['sccp'] = {}
            else:
                raise errors.invalid_choice('line_protocol', ['sip', 'sccp'])

        if self.columns_have_values('exten'):
            parsed['extension'] = {
                'exten': self.parse_unicode('exten'),
                'context': self.parse_unicode('context')
            }

        if self.columns_have_values('incall_exten', 'incall_context'):
            parsed['incall'] = {
                'exten': self.parse_unicode('incall_exten'),
                'context': self.parse_unicode('incall_context'),
                'ring_seconds': self.parse_unicode('incall_ring_seconds'),
            }

        if self.columns_have_values('cti_profile_name'):
            parsed['cti_profile'] = {
                'name': self.parse_unicode('cti_profile_name'),
                'enabled': self.parse_bool('cti_profile_enabled')
            }

        return parsed

    def columns_have_values(self, *columns):
        columns = set(columns)
        has_columns = set(self.fields.keys()).issuperset(columns)

        values = set(self.fields.get(column, "") for column in columns)
        has_values = values != set([""])

        return has_columns and has_values

    def parse_unicode(self, field):
        value = self.fields.get(field, "")
        if value != "":
            return value
        return None

    def parse_bool(self, field):
        value = self.fields.get(field, "")
        if value == "":
            return None
        if value not in ("0", "1"):
            raise errors.invalid_choice(field, ["0", "1"])
        return value == "1"

    def parse_int(self, field):
        value = self.fields.get(field, "")
        if value == "":
            return None
        if not value.isdigit():
            raise errors.wrong_type(field, 'integer')
        return int(value)

    def format_error(self, position, exc):
        return {'message': unicode(exc),
                'timestamp': int(time.time()),
                'details': {'row': self.fields,
                            'row_number': position}}


def parse():
    charset = request.mimetype_params.get('charset', 'utf-8')
    lines = request.data.split("\n")
    return CsvParser(lines, charset)
