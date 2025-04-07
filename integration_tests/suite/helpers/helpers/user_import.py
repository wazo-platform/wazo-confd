# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import csv
from io import StringIO

from .. import config
from . import call_permission, extension, new_client, voicemail, words


def csv_client():
    new_client.headers = {
        "Content-Type": "text/csv; charset=utf-8",
        "X-Auth-Token": config.TOKEN,
    }
    new_client.encoder = generate_csv
    return new_client


def generate_csv(rows):
    header = set()
    for row in rows:
        keys = set(key for key in row.keys())
        header.update(keys)

    output = StringIO()
    writer = csv.DictWriter(output, header)
    writer.writeheader()

    for row in rows:
        row = {key: str(value) for key, value in row.items()}
        writer.writerow(row)

    return output.getvalue().encode('utf-8')


def generate_entry(**params):
    entry = make_entry(params)
    response = csv_client().post("/users/import", [entry])
    entry.update(response.item['created'][0])
    return entry


def make_entry(params):
    entry = {
        'firstname': params.get('firstname', words.name()),
        'lastname': params.get('lastname', words.name()),
        'username': params.get('username', words.alphanumeric()),
        'password': params.get('password', words.alphanumeric()),
        'email': params.get('email', '{}@example.com'.format(words.alphanumeric())),
    }

    if params.get('voicemail'):
        name = "{e[firstname]} {e[lastname]}".format(e=entry)
        number = voicemail.find_available_number(config.CONTEXT)

        entry['voicemail_name'] = params.get('voicemail_name', name)
        entry['voicemail_number'] = params.get('voicemail_number', number)
        entry['voicemail_context'] = params.get('voicemail_context', config.CONTEXT)

    if params.get('line_protocol'):
        entry['line_protocol'] = params['line_protocol']
        entry['context'] = params.get('context', config.CONTEXT)

    if params.get('line_protocol') == 'sip':
        if 'sip_username' in params:
            entry['sip_username'] = params['sip_username']
        if 'sip_password' in params:
            entry['sip_password'] = params['sip_password']

    if params.get('extension'):
        exten = extension.find_available_exten(config.CONTEXT)
        entry.setdefault('line_protocol', 'sip')
        entry.setdefault('context', config.CONTEXT)
        entry['exten'] = params.get('exten', exten)

    if params.get('incall'):
        exten = extension.find_available_exten(config.INCALL_CONTEXT)
        entry['incall_exten'] = params.get('incall_exten', exten)
        entry['incall_context'] = params.get('incall_context', config.INCALL_CONTEXT)

    nb_permissions = params.pop('call_permissions', 0)
    if nb_permissions > 0:
        permissions = [
            call_permission.generate_call_permission() for _ in range(nb_permissions)
        ]
        entry['call_permissions'] = ';'.join(p['name'] for p in permissions)

    return entry
