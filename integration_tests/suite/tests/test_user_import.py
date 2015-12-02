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

from __future__ import unicode_literals

import csv
from cStringIO import StringIO

from hamcrest import assert_that, contains, has_entries, contains_string, instance_of, has_items, greater_than

from test_api import confd
from test_api import config
from test_api.setup import new_client
from test_api import helpers as h


def generate_csv(rows):
    header = set()
    for row in rows:
        keys = set(key.encode("utf8") for key in row.keys())
        header.update(keys)

    output = StringIO()
    writer = csv.DictWriter(output, header)
    writer.writeheader()

    for row in rows:
        row = {key.encode("utf8"): value.encode("utf8")
               for key, value in row.iteritems()}
        writer.writerow(row)

    return output.getvalue()


def assert_response_has_id(response, field, row_number=1):
    expected_entry = has_entries({'row_number': row_number,
                                  field: greater_than(0)})
    assert_that(response.item['created'], contains(expected_entry))


def assert_error_message(response, message, row_number=1):
    response.assert_status(400)
    expected_error = has_entries({'timestamp': instance_of(int),
                                  'details': has_entries(row_number=row_number),
                                  'message': contains_string(message)})
    assert_that(response.json['errors'], contains(expected_error))


client = new_client(headers={"Content-Type": "text/csv; charset=utf-8"},
                    encoder=generate_csv)


def test_given_required_fields_missing_then_error_returned():
    csv = [{"lastname": "missingfirstname"}]

    response = client.post("/users/import", csv)
    assert_error_message(response, "firstname")


def test_given_csv_has_minimal_fields_for_a_user_then_user_imported():
    csv = [{"firstname": "Rîchard"}]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'user_id')

    user_id = response.item['created'][0]['user_id']
    user = confd.users(user_id).get().item

    assert_that(user, has_entries(firstname="Rîchard"))


def test_given_csv_has_all_fields_for_a_user_then_user_imported():
    csv = [{"firstname": "Rîchard",
            "lastname": "Lâpointe",
            "entity_id": "1",
            "language": "fr_FR",
            "username": "richardlapointe",
            "password": "secret",
            "outgoing_caller_id": '"Rîchy Cool" <4185551234>',
            "mobile_phone_number": "4181234567",
            "supervision_enabled": "1",
            "call_transfer_enabled": "0",
            "simultaneous_calls": "5",
            "ring_seconds": "10",
            "userfield": "userfield",
            }]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'user_id')

    user_id = response.item['created'][0]['user_id']
    user = confd.users(user_id).get().item

    assert_that(user, has_entries(firstname="Rîchard",
                                  lastname="Lâpointe",
                                  language="fr_FR",
                                  username="richardlapointe",
                                  password="secret",
                                  outgoing_caller_id='"Rîchy Cool" <4185551234>',
                                  mobile_phone_number="4181234567",
                                  supervision_enabled=True,
                                  call_transfer_enabled=False,
                                  simultaneous_calls=5,
                                  ring_seconds=10,
                                  userfield="userfield"))


def test_given_csv_column_has_wrong_type_then_error_returned():
    csv = [{'firstname': 'invalidbool',
            'supervision_enabled': 'yeah'}]

    response = client.post("/users/import", csv)
    assert_error_message(response, 'supervision_enabled')


def test_given_user_contains_error_then_error_returned():
    csv = [{"firstname": "richard",
            "mobile_phone_number": "blah"}]

    response = client.post("/users/import", csv)
    assert_error_message(response, 'mobile_phone_number')


def test_given_csv_has_minimal_voicemail_fields_then_voicemail_imported():
    number, context = h.voicemail.generate_number_and_context()
    csv = [{"firstname": "Jôey",
            "voicemail_name": "Jôey VM",
            "voicemail_number": number,
            "voicemail_context": context}]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'voicemail_id')

    voicemail_id = response.item['created'][0]['voicemail_id']
    voicemail = confd.voicemails(voicemail_id).get().item

    assert_that(voicemail, has_entries(name="Jôey VM",
                                       number=number,
                                       context=context))


def test_given_csv_has_all_voicemail_fields_then_voicemail_imported():
    number, context = h.voicemail.generate_number_and_context()
    csv = [{"firstname": "Jôey",
            "voicemail_name": "Jôey VM",
            "voicemail_number": number,
            "voicemail_context": context,
            "voicemail_password": "1234",
            "voicemail_email": "email@example.com",
            "voicemail_attach_audio": "0",
            "voicemail_delete_messages": "1",
            "voicemail_ask_password": "0",
            }]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'voicemail_id')

    voicemail_id = response.item['created'][0]['voicemail_id']
    voicemail = confd.voicemails(voicemail_id).get().item

    assert_that(voicemail, has_entries(name="Jôey VM",
                                       number=number,
                                       context=context,
                                       password="1234",
                                       email='email@example.com',
                                       attach_audio=False,
                                       delete_messages=True,
                                       ask_password=False))


def test_given_voicemail_contains_error_then_error_returned():
    csv = [{"firstname": "Jôey",
            "voicemail_name": "Jôey VM",
            "voicemail_number": "",
            "voicemail_context": ""}]

    response = client.post("/users/import", csv)
    assert_error_message(response, 'number')


def test_given_csv_has_minimal_line_fields_then_line_created():
    csv = [{"firstname": "Chârles",
            "line_protocol": "sip",
            "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'line_id')

    line_id = response.item['created'][0]['line_id']

    line = confd.lines(line_id).get().item
    assert_that(line, has_entries(context=config.CONTEXT,
                                  protocol='sip'))


def test_given_line_has_error_then_error_returned():
    csv = [{"firstname": "Chârles",
            "line_protocol": "sip",
            "context": 'invalidcontext'}]

    response = client.post("/users/import", csv)
    assert_error_message(response, 'context')


def test_given_csv_has_minimal_sip_fields_then_sip_endpoint_created():
    csv = [{"firstname": "Chârles",
            "line_protocol": "sip",
            "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'sip_id')

    sip_id = response.item['created'][0]['sip_id']

    sip = confd.endpoints.sip(sip_id).get().item
    assert_that(sip, has_entries(id=sip_id))


def test_given_csv_has_all_sip_fields_then_sip_endpoint_created():
    csv = [{"firstname": "Chârles",
            "line_protocol": "sip",
            "context": config.CONTEXT,
            "sip_username": "sipusername",
            "sip_secret": "sipsecret"}]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'sip_id')

    sip_id = response.item['created'][0]['sip_id']

    sip = confd.endpoints.sip(sip_id).get().item
    assert_that(sip, has_entries(username="sipusername",
                                 secret="sipsecret"))


def test_given_csv_has_minimal_sccp_fields_then_sccp_endpoint_created():
    csv = [{"firstname": "Chârles",
            "line_protocol": "sccp",
            "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'sccp_id')

    sccp_id = response.item['created'][0]['sccp_id']

    sccp = confd.endpoints.sccp(sccp_id).get().item
    assert_that(sccp, has_entries(id=sccp_id))


def test_given_csv_has_extension_fields_then_extension_created():
    exten = h.extension.find_available_exten(config.CONTEXT)
    csv = [{"firstname": "Géorge",
            "line_protocol": "sip",
            "exten": exten,
            "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'extension_id')

    extension_id = response.item['created'][0]['extension_id']
    extension = confd.extensions(extension_id).get().item

    assert_that(extension, has_entries(exten=exten,
                                       context=config.CONTEXT))


def test_given_csv_extension_has_errors_then_errors_returned():
    csv = [{"firstname": "Géorge",
            "line_protocol": "sip",
            "exten": "9999",
            "context": "invalid"}]

    response = client.post("/users/import", csv)
    assert_error_message(response, 'context')


def test_given_csv_has_minimal_incall_fields_then_incall_created():
    exten = h.extension.find_available_exten('from-extern')
    csv = [{"firstname": "Pâscal",
            "line_protocol": "sccp",
            "context": config.CONTEXT,
            "incall_exten": exten,
            "incall_context": "from-extern"}]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'incall_extension_id')

    incall_extension_id = response.item['created'][0]['incall_extension_id']
    extension = confd.extensions(incall_extension_id).get().item

    assert_that(extension, has_entries(exten=exten,
                                       context="from-extern"))


def test_given_csv_has_all_incall_fields_then_incall_created():
    exten = h.extension.find_available_exten('from-extern')
    csv = [{"firstname": "Pâscal",
            "line_protocol": "sccp",
            "context": config.CONTEXT,
            "incall_exten": exten,
            "incall_context": "from-extern",
            "incall_ring_seconds": "10"}]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'incall_extension_id')


def test_given_csv_incall_has_errors_then_errors_returned():
    csv = [{"firstname": "Géorge",
            "line_protocol": "sip",
            "context": config.CONTEXT,
            "incall_exten": "9999",
            "incall_context": "invalid"}]

    response = client.post("/users/import", csv)
    assert_error_message(response, 'context')


def test_given_csv_has_cti_fields_then_cti_profile_associated():
    csv = [{"firstname": "Thômas",
            "username": "thomas",
            "password": "secret",
            "cti_profile_enabled": "1",
            "cti_profile_name": "Client"}]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'cti_profile_id')

    user_id = response.item['created'][0]['user_id']
    user_cti_profile = confd.users(user_id).cti.get().item

    assert_that(user_cti_profile, has_entries(cti_profile_id=greater_than(0),
                                              enabled=True))


def test_given_csv_cti_profile_has_errors_then_errors_returned():
    csv = [{"firstname": "Thômas",
            "username": "thomas",
            "password": "secret",
            "cti_profile_enabled": "1",
            "cti_profile_name": "InvalidProfile"}]

    response = client.post("/users/import", csv)
    assert_error_message(response, 'CtiProfile')


def test_given_csv_has_all_resources_then_all_relations_created():
    exten = h.extension.find_available_exten(config.CONTEXT)
    incall_exten = h.extension.find_available_exten('from-extern')
    vm_number = h.voicemail.find_available_number(config.CONTEXT)

    csv = [{"firstname": "Frânçois",
            "exten": exten,
            "context": config.CONTEXT,
            "line_protocol": "sip",
            "incall_exten": incall_exten,
            "incall_context": 'from-extern',
            "voicemail_name": "francois",
            "voicemail_number": vm_number,
            "voicemail_context": config.CONTEXT,
            "cti_profile_name": "Client",
            }]

    response = client.post("/users/import", csv)
    assert_response_has_id(response, 'user_id')
    assert_response_has_id(response, 'line_id')
    assert_response_has_id(response, 'voicemail_id')
    assert_response_has_id(response, 'extension_id')
    assert_response_has_id(response, 'incall_extension_id')
    assert_response_has_id(response, 'sip_id')
    assert_response_has_id(response, 'cti_profile_id')

    entry = response.item['created'][0]

    response = confd.users(entry['user_id']).lines.get()
    assert_that(response.items, contains(has_entries(line_id=entry['line_id'])))

    response = confd.lines(entry['line_id']).extensions.get()
    assert_that(response.items, has_items(has_entries(extension_id=entry['extension_id']),
                                          has_entries(extension_id=entry['incall_extension_id'])))

    response = confd.users(entry['user_id']).voicemail.get()
    assert_that(response.item, has_entries(voicemail_id=entry['voicemail_id']))

    response = confd.lines(entry['line_id']).endpoints.sip.get()
    assert_that(response.item, has_entries(endpoint='sip',
                                           endpoint_id=entry['sip_id']))

    response = confd.users(entry['user_id']).cti.get()
    assert_that(response.item, has_entries(cti_profile_id=entry['cti_profile_id']))
