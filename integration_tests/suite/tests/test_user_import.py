# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from hamcrest import (assert_that,
                      contains,
                      contains_string,
                      equal_to,
                      greater_than,
                      has_entries,
                      has_items,
                      has_length,
                      not_none,
                      none,
                      instance_of)

from test_api import confd
from test_api import config
from test_api import helpers as h
from test_api import fixtures


client = h.user_import.csv_client()


def get_import_field(response, fieldname, row_number=1):
    rows = response.item['created']
    assert_that(rows,
                has_length(row_number),
                "CSV import did not create enough rows")

    row = rows[row_number - 1]
    assert_that(row,
                has_entries({'row_number': row_number,
                             fieldname: not_none()}))

    return row[fieldname]


def assert_response_has_id(response, field, row_number=1):
    expected_entry = has_entries({'row_number': row_number,
                                  field: greater_than(0)})
    assert_that(response.item['created'], contains(expected_entry))


def assert_error(response, expect):
    response.assert_status(400)
    assert_that(response.json, has_entries(errors=expect))


def has_error_field(fieldname, row_number=1):
    return contains(has_entries(timestamp=instance_of(int),
                                details=has_entries(row_number=row_number),
                                message=contains_string(fieldname)))


def test_given_required_fields_missing_then_error_returned():
    csv = [{"lastname": "missingfirstname"}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field("firstname"))


def test_given_entity_id_does_not_exist_then_error_returned():
    csv = [{"firstname": "entityfirstname",
            "entity_id": "999999999"}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field("entity"))


def test_given_csv_has_minimal_fields_for_a_user_then_user_imported():
    csv = [{"firstname": "Rîchard"}]

    response = client.post("/users/import", csv)
    user_id = get_import_field(response, 'user_id')
    user_uuid = get_import_field(response, 'user_uuid')

    user = confd.users(user_id).get().item
    assert_that(user, has_entries(firstname="Rîchard", uuid=user_uuid))


def test_given_csv_has_all_fields_for_a_user_then_user_imported():
    csv = [{"firstname": "Rîchard",
            "lastname": "Lâpointe",
            "email": "richard@lapointe.org",
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
    user_id = get_import_field(response, 'user_id')
    user_uuid = get_import_field(response, 'user_uuid')

    user = confd.users(user_id).get().item
    assert_that(user, has_entries(firstname="Rîchard",
                                  lastname="Lâpointe",
                                  email="richard@lapointe.org",
                                  language="fr_FR",
                                  username="richardlapointe",
                                  password="secret",
                                  outgoing_caller_id='"Rîchy Cool" <4185551234>',
                                  mobile_phone_number="4181234567",
                                  supervision_enabled=True,
                                  call_transfer_enabled=False,
                                  simultaneous_calls=5,
                                  ring_seconds=10,
                                  userfield="userfield",
                                  uuid=user_uuid))


def test_given_csv_column_has_wrong_type_then_error_returned():
    csv = [{'firstname': 'invalidbool',
            'supervision_enabled': 'yeah'}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('supervision_enabled'))


def test_given_user_contains_error_then_error_returned():
    csv = [{"firstname": "richard",
            "mobile_phone_number": "blah"}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('mobile_phone_number'))


def test_given_csv_has_minimal_voicemail_fields_then_voicemail_imported():
    number, context = h.voicemail.generate_number_and_context()
    csv = [{"firstname": "Jôey",
            "voicemail_name": "Jôey VM",
            "voicemail_number": number,
            "voicemail_context": context}]

    response = client.post("/users/import", csv)
    voicemail_id = get_import_field(response, 'voicemail_id')

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
    voicemail_id = get_import_field(response, 'voicemail_id')

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
            "voicemail_number": "%%%$",
            "voicemail_context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('number'))


def test_given_csv_has_minimal_line_fields_then_line_created():
    csv = [{"firstname": "Chârles",
            "line_protocol": "sip",
            "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    line_id = get_import_field(response, 'line_id')

    line = confd.lines(line_id).get().item
    assert_that(line, has_entries(context=config.CONTEXT,
                                  protocol='sip'))


def test_given_line_has_error_then_error_returned():
    csv = [{"firstname": "Chârles",
            "line_protocol": "sip",
            "context": 'invalidcontext'}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('context'))


def test_given_csv_has_minimal_sip_fields_then_sip_endpoint_created():
    csv = [{"firstname": "Chârles",
            "line_protocol": "sip",
            "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    sip_id = get_import_field(response, 'sip_id')

    sip = confd.endpoints.sip(sip_id).get().item
    assert_that(sip, has_entries(id=sip_id))


def test_given_csv_has_all_sip_fields_then_sip_endpoint_created():
    csv = [{"firstname": "Chârles",
            "line_protocol": "sip",
            "context": config.CONTEXT,
            "sip_username": "sipusername",
            "sip_secret": "sipsecret"}]

    response = client.post("/users/import", csv)
    sip_id = get_import_field(response, 'sip_id')

    sip = confd.endpoints.sip(sip_id).get().item
    assert_that(sip, has_entries(username="sipusername",
                                 secret="sipsecret"))


def test_given_csv_has_minimal_sccp_fields_then_sccp_endpoint_created():
    csv = [{"firstname": "Chârles",
            "line_protocol": "sccp",
            "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    sccp_id = get_import_field(response, 'sccp_id')

    sccp = confd.endpoints.sccp(sccp_id).get().item
    assert_that(sccp, has_entries(id=sccp_id))


def test_given_csv_has_extension_fields_then_extension_created():
    exten = h.extension.find_available_exten(config.CONTEXT)
    csv = [{"firstname": "Géorge",
            "line_protocol": "sip",
            "exten": exten,
            "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    extension_id = get_import_field(response, 'extension_id')

    extension = confd.extensions(extension_id).get().item
    assert_that(extension, has_entries(exten=exten,
                                       context=config.CONTEXT))


def test_given_csv_extension_has_errors_then_errors_returned():
    csv = [{"firstname": "Géorge",
            "line_protocol": "sip",
            "exten": "9999",
            "context": "invalid"}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('context'))


def test_given_csv_has_minimal_incall_fields_then_incall_created():
    exten = h.extension.find_available_exten(config.INCALL_CONTEXT)
    csv = [{"firstname": "Pâscal",
            "line_protocol": "sccp",
            "context": config.CONTEXT,
            "incall_exten": exten,
            "incall_context": config.INCALL_CONTEXT}]

    response = client.post("/users/import", csv)
    incall_extension_id = get_import_field(response, 'incall_extension_id')

    extension = confd.extensions(incall_extension_id).get().item
    assert_that(extension, has_entries(exten=exten,
                                       context=config.INCALL_CONTEXT))


def test_given_csv_has_all_incall_fields_then_incall_created():
    exten = h.extension.find_available_exten(config.INCALL_CONTEXT)
    csv = [{"firstname": "Pâscal",
            "line_protocol": "sccp",
            "context": config.CONTEXT,
            "incall_exten": exten,
            "incall_context": config.INCALL_CONTEXT,
            "incall_ring_seconds": "10"}]

    response = client.post("/users/import", csv)
    get_import_field(response, 'incall_extension_id')


def test_given_csv_incall_has_errors_then_errors_returned():
    csv = [{"firstname": "Géorge",
            "line_protocol": "sip",
            "context": config.CONTEXT,
            "incall_exten": "9999",
            "incall_context": "invalid"}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('context'))


def test_given_csv_has_cti_fields_then_cti_profile_associated():
    csv = [{"firstname": "Thômas",
            "username": "thomas",
            "password": "secret",
            "cti_profile_enabled": "1",
            "cti_profile_name": "Client"}]

    response = client.post("/users/import", csv)
    cti_profile_id = get_import_field(response, 'cti_profile_id')
    user_id = get_import_field(response, 'user_id')

    user_cti_profile = confd.users(user_id).cti.get().item
    assert_that(user_cti_profile, has_entries(cti_profile_id=cti_profile_id,
                                              enabled=True))


def test_given_csv_cti_profile_has_errors_then_errors_returned():
    csv = [{"firstname": "Thômas",
            "username": "thomas",
            "password": "secret",
            "cti_profile_enabled": "1",
            "cti_profile_name": "InvalidProfile"}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('CtiProfile'))


def test_given_csv_has_all_resources_then_all_relations_created():
    exten = h.extension.find_available_exten(config.CONTEXT)
    incall_exten = h.extension.find_available_exten(config.INCALL_CONTEXT)
    vm_number = h.voicemail.find_available_number(config.CONTEXT)

    csv = [{"firstname": "Frânçois",
            "exten": exten,
            "context": config.CONTEXT,
            "line_protocol": "sip",
            "incall_exten": incall_exten,
            "incall_context": config.INCALL_CONTEXT,
            "voicemail_name": "francois",
            "voicemail_number": vm_number,
            "voicemail_context": config.CONTEXT,
            "cti_profile_name": "Client",
            }]

    response = client.post("/users/import", csv)

    user_id = get_import_field(response, 'user_id')
    line_id = get_import_field(response, 'line_id')
    voicemail_id = get_import_field(response, 'voicemail_id')
    extension_id = get_import_field(response, 'extension_id')
    incall_extension_id = get_import_field(response, 'incall_extension_id')
    sip_id = get_import_field(response, 'sip_id')
    cti_profile_id = get_import_field(response, 'cti_profile_id')

    response = confd.users(user_id).lines.get()
    assert_that(response.items, contains(has_entries(line_id=line_id)))

    response = confd.lines(line_id).extensions.get()
    assert_that(response.items, has_items(has_entries(extension_id=extension_id),
                                          has_entries(extension_id=incall_extension_id)))

    response = confd.users(user_id).voicemail.get()
    assert_that(response.item, has_entries(voicemail_id=voicemail_id))

    response = confd.lines(line_id).endpoints.sip.get()
    assert_that(response.item, has_entries(endpoint='sip',
                                           endpoint_id=sip_id))

    response = confd.users(user_id).cti.get()
    assert_that(response.item, has_entries(cti_profile_id=cti_profile_id))


@fixtures.sip()
@fixtures.extension()
@fixtures.extension(context=config.INCALL_CONTEXT)
@fixtures.voicemail()
def test_given_resources_alreay_exist_when_importing_then_resources_associated(sip, extension, incall, voicemail):
    cti_profile = h.cti_profile.find_by_name("Client")

    csv = [{"firstname": "importassociate",
            "exten": extension['exten'],
            "context": extension['context'],
            "line_protocol": "sip",
            "sip_username": sip['username'],
            "incall_exten": incall['exten'],
            "incall_context": incall['context'],
            "voicemail_number": voicemail['number'],
            "voicemail_context": voicemail['context'],
            "cti_profile_name": "Client",
            }]

    response = client.post("/users/import", csv)

    user_id = get_import_field(response, 'user_id')
    line_id = get_import_field(response, 'line_id')

    response = confd.users(user_id).lines.get()
    assert_that(response.items, contains(has_entries(line_id=line_id)))

    response = confd.lines(line_id).extensions.get()
    assert_that(response.items, has_items(has_entries(extension_id=extension['id']),
                                          has_entries(extension_id=incall['id'])))

    response = confd.users(user_id).voicemail.get()
    assert_that(response.item, has_entries(voicemail_id=voicemail['id']))

    response = confd.lines(line_id).endpoints.sip.get()
    assert_that(response.item, has_entries(endpoint='sip',
                                           endpoint_id=sip['id']))

    response = confd.users(user_id).cti.get()
    assert_that(response.item, has_entries(cti_profile_id=cti_profile['id']))


def test_given_csv_has_more_than_one_entry_then_all_entries_imported():
    exten1 = h.extension.find_available_exten(config.CONTEXT)
    incall_exten1 = h.extension.find_available_exten('from-extern')
    vm_number1 = h.voicemail.find_available_number(config.CONTEXT)

    exten2 = h.extension.find_available_exten(config.CONTEXT, exclude=[exten1])
    incall_exten2 = h.extension.find_available_exten('from-extern', exclude=[incall_exten1])
    vm_number2 = h.voicemail.find_available_number(config.CONTEXT, exclude=[vm_number1])

    csv = [
        {"entity_id": "1",
         "firstname": "Jèan",
         "lastname": "Bâptiste",
         "email": "jean@baptiste.st",
         "mobile_phone_number": "5551234567",
         "ring_seconds": "15",
         "simultaneous_calls": "10",
         "language": "fr_FR",
         "outgoing_caller_id": '"Jean Le Grand" <5557654321>',
         "userfield": "userfield",
         "supervision_enabled": "1",
         "call_transfer_enabled": "1",
         "exten": exten1,
         "context": config.CONTEXT,
         "line_protocol": "sip",
         "sip_username": "jeansipusername",
         "sip_password": "jeansippassword",
         "incall_exten": incall_exten1,
         "incall_context": 'from-extern',
         "incall_ring_seconds": "10",
         "voicemail_name": "jean",
         "voicemail_number": vm_number1,
         "voicemail_context": config.CONTEXT,
         "voicemail_password": "1234",
         "voicemail_email": "test@example.com",
         "voicemail_attach_audio": "1",
         "voicemail_delete_messages": "1",
         "voicemail_ask_password": "1",
         "cti_profile_name": "Client",
         "cti_profile_enabled": "1",
         "username": "jean",
         "password": "secret"},
        {"entity_id": "1",
         "firstname": "Moùssa",
         "lastname": "Nôbamgo",
         "email": "moussa@nobamgo.ta",
         "mobile_phone_number": "5553456789",
         "ring_seconds": "20",
         "simultaneous_calls": "8",
         "language": "fr_FR",
         "outgoing_caller_id": '"Mousssssssaaaa" <5557654321>',
         "userfield": "userfield",
         "supervision_enabled": "1",
         "call_transfer_enabled": "1",
         "exten": exten2,
         "context": config.CONTEXT,
         "line_protocol": "sccp",
         "incall_exten": incall_exten2,
         "incall_context": 'from-extern',
         "incall_ring_seconds": "12",
         "voicemail_name": "moussa",
         "voicemail_number": vm_number2,
         "voicemail_context": config.CONTEXT,
         "voicemail_password": "2345",
         "voicemail_email": "test2@example.com",
         "voicemail_attach_audio": "1",
         "voicemail_delete_messages": "1",
         "voicemail_ask_password": "1",
         "cti_profile_name": "Client",
         "cti_profile_enabled": "1",
         "username": "moussa",
         "password": "secret"},
    ]

    response = client.post("/users/import", csv)

    assert_that(len(response.item['created']), equal_to(2))


def test_given_field_group_is_empty_then_resource_is_not_created():
    group = {"cti_profile_enabled": "",
             "cti_profile_name": "",
             "username": "",
             "password": ""}
    yield import_empty_group, group, 'cti_profile_id'

    group = {"voicemail_name": "",
             "voicemail_number": "",
             "voicemail_context": "",
             "voicemail_password": "",
             "voicemail_email": "",
             "voicemail_attach_audio": "",
             "voicemail_delete_messages": "",
             "voicemail_ask_password": ""}
    yield import_empty_group, group, 'voicemail_id'

    group = {"line_protocol": ""}
    yield import_empty_group, group, 'line_id'

    group = {"line_protocol": "sip",
             "exten": "",
             "context": ""}
    yield import_empty_group, group, 'extension_id'

    exten = h.extension.find_available_exten(config.CONTEXT)
    group = {"line_protocol": "sip",
             "exten": exten,
             "context": config.CONTEXT,
             "incall_exten": "",
             "incall_context": ""}
    yield import_empty_group, group, 'incall_extension_id'


def import_empty_group(fields, parameter):
    fields['firstname'] = "Abigaël"

    response = client.post("/users/import", [fields])
    entry = response.item['created'][0]

    assert_that(entry, has_entries({parameter: none()}))


@fixtures.csv_entry()
def test_when_updating_user_fields_then_user_resource_updated(entry):
    csv = [{"uuid": entry['user_uuid'],
            "firstname": "Joël",
            "lastname": "Làchance",
            "language": "fr_FR",
            "email": "joel@lachance.fr",
            "username": "joellachance",
            "password": "secret",
            "outgoing_caller_id": '"Joël Spîffy" <4185551234>',
            "mobile_phone_number": "4181234567",
            "supervision_enabled": "1",
            "call_transfer_enabled": "0",
            "simultaneous_calls": "5",
            "ring_seconds": "10",
            "userfield": "userfield",
            }]

    response = client.put("/users/import", csv)
    response.assert_ok()

    user_id = response.item['updated'][0]['user_id']
    user_uuid = response.item['updated'][0]['user_uuid']
    user = confd.users(user_id).get().item

    assert_that(user, has_entries(firstname="Joël",
                                  lastname="Làchance",
                                  email="joel@lachance.fr",
                                  language="fr_FR",
                                  username="joellachance",
                                  password="secret",
                                  outgoing_caller_id='"Joël Spîffy" <4185551234>',
                                  mobile_phone_number="4181234567",
                                  supervision_enabled=True,
                                  call_transfer_enabled=False,
                                  simultaneous_calls=5,
                                  ring_seconds=10,
                                  userfield="userfield",
                                  uuid=user_uuid))


@fixtures.csv_entry(voicemail=True)
def test_when_updating_voicemail_fields_then_voicemail_updated(entry):
    number = h.voicemail.find_available_number(config.CONTEXT)

    csv = [{"uuid": entry["user_uuid"],
            "voicemail_name": "Jôey VM",
            "voicemail_number": number,
            "voicemail_context": config.CONTEXT,
            "voicemail_password": "1234",
            "voicemail_email": "email@example.com",
            "voicemail_attach_audio": "0",
            "voicemail_delete_messages": "1",
            "voicemail_ask_password": "0",
            }]

    response = client.put("/users/import", csv)
    response.assert_ok()

    voicemail_id = response.item['updated'][0]['voicemail_id']
    voicemail = confd.voicemails(voicemail_id).get().item

    assert_that(voicemail, has_entries(name="Jôey VM",
                                       number=number,
                                       context=config.CONTEXT,
                                       password="1234",
                                       email='email@example.com',
                                       attach_audio=False,
                                       delete_messages=True,
                                       ask_password=False))


@fixtures.csv_entry()
def test_when_adding_voicemail_fields_then_voicemail_created(entry):
    number = h.voicemail.find_available_number(config.CONTEXT)

    csv = [{"uuid": entry['user_uuid'],
            "voicemail_name": "Jôey VM",
            "voicemail_number": number,
            "voicemail_context": config.CONTEXT,
            "voicemail_password": "1234",
            "voicemail_email": "email@example.com",
            "voicemail_attach_audio": "0",
            "voicemail_delete_messages": "1",
            "voicemail_ask_password": "0",
            }]

    response = client.put("/users/import", csv)
    response.assert_ok()

    voicemail_id = response.item['updated'][0]['voicemail_id']
    voicemail = confd.voicemails(voicemail_id).get().item

    assert_that(voicemail, has_entries(name="Jôey VM",
                                       number=number,
                                       context=config.CONTEXT,
                                       password="1234",
                                       email='email@example.com',
                                       attach_audio=False,
                                       delete_messages=True,
                                       ask_password=False))


@fixtures.csv_entry(line_protocol="sip")
def test_when_updating_sip_line_fields_then_sip_updated(entry):
    csv = [{"uuid": entry["user_uuid"],
            "sip_username": "mynewsipusername",
            "sip_secret": "mynewsippassword",
            }]

    response = client.put("/users/import", csv)

    sip_id = response.item['updated'][0]['sip_id']
    sip = confd.endpoints.sip(sip_id).get().item

    assert_that(sip, has_entries(username="mynewsipusername",
                                 secret="mynewsippassword"))


@fixtures.csv_entry()
def test_when_adding_sip_line_then_sip_created(entry):
    csv = [{"uuid": entry["user_uuid"],
            "line_protocol": "sip",
            "sip_username": "createdsipusername",
            "sip_secret": "createdsippassword",
            }]

    response = client.put("/users/import", csv)

    sip_id = response.item['updated'][0]['sip_id']
    sip = confd.endpoints.sip(sip_id).get().item

    assert_that(sip, has_entries(username="createdsipusername",
                                 secret="createdsippassword"))


@fixtures.csv_entry()
def test_when_adding_sccp_line_then_sccp_created(entry):
    csv = [{"uuid": entry["user_uuid"],
            "line_protocol": "sccp",
            }]

    response = client.put("/users/import", csv)

    sccp_id = response.item['updated'][0]['sccp_id']
    sccp = confd.endpoints.sccp(sccp_id).get().item

    assert_that(sccp, has_entries(id=sccp_id))


@fixtures.csv_entry(line_protocol="sip")
def test_when_changing_line_protocol_then_error_raised(entry):
    csv = [{"uuid": entry["user_uuid"],
            "line_protocol": "sccp",
            }]

    response = client.put("/users/import", csv)

    assert_error(response, has_error_field('endpoint'))


@fixtures.csv_entry(extension=True)
def test_when_updating_extension_then_extension_updated(entry):
    exten = h.extension.find_available_exten(config.CONTEXT)

    csv = [{"uuid": entry["user_uuid"],
            "exten": exten,
            "context": config.CONTEXT,
            }]

    response = client.put("/users/import", csv)

    extension_id = response.item['updated'][0]['extension_id']
    extension = confd.extensions(extension_id).get().item

    assert_that(extension, has_entries(exten=exten,
                                       context=config.CONTEXT))


@fixtures.csv_entry(line_protocol="sip")
def test_when_adding_extension_then_extension_created(entry):
    exten = h.extension.find_available_exten(config.CONTEXT)

    csv = [{"uuid": entry["user_uuid"],
            "exten": exten,
            "context": config.CONTEXT,
            }]

    response = client.put("/users/import", csv)

    extension_id = response.item['updated'][0]['extension_id']
    extension = confd.extensions(extension_id).get().item

    assert_that(extension, has_entries(exten=exten,
                                       context=config.CONTEXT))


@fixtures.csv_entry(incall=True)
def test_when_updating_incall_fields_then_incall_updated(entry):
    exten = h.extension.find_available_exten(config.INCALL_CONTEXT)

    csv = [{"uuid": entry["user_uuid"],
            "incall_exten": exten,
            "incall_context": config.INCALL_CONTEXT,
            "incall_ring_seconds": "10"}]

    response = client.put("/users/import", csv)

    incall_id = response.item['updated'][0]['incall_extension_id']
    extension = confd.extensions(incall_id).get().item

    assert_that(extension, has_entries(exten=exten,
                                       context=config.INCALL_CONTEXT))


@fixtures.csv_entry(line_protocol="sip", extension=True)
def test_when_adding_incall_then_incall_created(entry):
    exten = h.extension.find_available_exten(config.INCALL_CONTEXT)

    csv = [{"uuid": entry["user_uuid"],
            "incall_exten": exten,
            "incall_context": config.INCALL_CONTEXT,
            "incall_ring_seconds": "10"}]

    response = client.put("/users/import", csv)

    incall_id = response.item['updated'][0]['incall_extension_id']
    extension = confd.extensions(incall_id).get().item

    assert_that(extension, has_entries(exten=exten,
                                       context=config.INCALL_CONTEXT))


@fixtures.csv_entry(cti_profile=True,
                    cti_profile_name="Client")
def test_when_updating_cti_profile_fields_then_cti_profile_updated(entry):
    csv = [{"uuid": entry['user_uuid'],
            "cti_profile_name": "Agent"}]

    response = client.put("/users/import", csv)

    user_id = response.item['updated'][0]['user_id']
    cti_profile_id = h.cti_profile.find_id_for_profile("Agent")

    user_cti_profile = confd.users(user_id).cti.get().item
    assert_that(user_cti_profile, has_entries(cti_profile_id=cti_profile_id,
                                              enabled=True))


@fixtures.csv_entry()
def test_when_adding_cti_profile_fields_then_cti_profile_added(entry):
    csv = [{"uuid": entry['user_uuid'],
            "cti_profile_name": "Agent",
            "cti_profile_enabled": "1"}]

    response = client.put("/users/import", csv)

    user_id = response.item['updated'][0]['user_id']
    cti_profile_id = h.cti_profile.find_id_for_profile("Agent")

    user_cti_profile = confd.users(user_id).cti.get().item
    assert_that(user_cti_profile, has_entries(cti_profile_id=cti_profile_id,
                                              enabled=True))


def check_error_on_update(entry, fields, error):
    entry = dict(entry)
    entry.update(fields)
    entry['uuid'] = entry['user_uuid']
    response = client.put("/users/import", [entry])
    assert_error(response, has_error_field(error))


def test_given_csv_has_errors_then_errors_returned():
    with fixtures.csv_entry(voicemail=True, incall=True,
                            cti_profile=True, line_protocol="sip") as entry:
        yield check_error_on_update, entry, {'firstname': ''}, 'firstname'
        yield check_error_on_update, entry, {'voicemail_number': '^]'}, 'number'
        yield check_error_on_update, entry, {'sip_username': '^]'}, 'name'
        yield check_error_on_update, entry, {'cti_profile_name': '^]'}, 'CtiProfile'


@fixtures.csv_entry(extension=True, voicemail=True, incall=True, cti_profile=True, line_protocol="sip")
@fixtures.csv_entry(extension=True, voicemail=True, incall=True, cti_profile=True, line_protocol="sccp")
def test_given_2_entries_in_csv_then_2_entries_updated(entry1, entry2):
    exten1 = h.extension.find_available_exten(config.CONTEXT)
    incall_exten1 = h.extension.find_available_exten(config.INCALL_CONTEXT)
    vm_number1 = h.voicemail.find_available_number(config.CONTEXT)

    exten2 = h.extension.find_available_exten(config.CONTEXT, exclude=[exten1])
    incall_exten2 = h.extension.find_available_exten(config.INCALL_CONTEXT, exclude=[incall_exten1])
    vm_number2 = h.voicemail.find_available_number(config.CONTEXT, exclude=[vm_number1])

    csv = [
        {"uuid": entry1["user_uuid"],
         "entity_id": "1",
         "exten": exten1,
         "context": config.CONTEXT,
         "firstname": "Géorge",
         "lastname": "Bâptiste",
         "email": "george@baptiste.st",
         "mobile_phone_number": "5551234567",
         "ring_seconds": "15",
         "simultaneous_calls": "10",
         "language": "fr_FR",
         "outgoing_caller_id": '"Géorge Le Grand" <5557654321>',
         "userfield": "userfield",
         "supervision_enabled": "1",
         "call_transfer_enabled": "1",
         "sip_username": "georgesipusername",
         "sip_password": "georgesippassword",
         "incall_exten": incall_exten1,
         "incall_context": config.INCALL_CONTEXT,
         "incall_ring_seconds": "10",
         "voicemail_name": "george",
         "voicemail_number": vm_number1,
         "voicemail_context": config.CONTEXT,
         "voicemail_password": "1234",
         "voicemail_email": "test@example.com",
         "voicemail_attach_audio": "1",
         "voicemail_delete_messages": "1",
         "voicemail_ask_password": "1",
         "cti_profile_name": "Agent",
         "cti_profile_enabled": "1",
         "username": "george",
         "password": "secret"},
        {"uuid": entry2['user_uuid'],
         "entity_id": "1",
         "firstname": "Moùssa",
         "lastname": "Nôbamgo",
         "email": "moussa@nobamgo.sd",
         "mobile_phone_number": "5553456789",
         "ring_seconds": "20",
         "simultaneous_calls": "8",
         "language": "fr_FR",
         "outgoing_caller_id": '"Mousssssssaaaa" <5557654321>',
         "userfield": "userfield",
         "supervision_enabled": "1",
         "call_transfer_enabled": "1",
         "exten": exten2,
         "context": config.CONTEXT,
         "incall_exten": incall_exten2,
         "incall_context": 'from-extern',
         "incall_ring_seconds": "12",
         "voicemail_name": "moussa",
         "voicemail_number": vm_number2,
         "voicemail_context": config.CONTEXT,
         "voicemail_password": "2345",
         "voicemail_email": "test2@example.com",
         "voicemail_attach_audio": "1",
         "voicemail_delete_messages": "1",
         "voicemail_ask_password": "1",
         "cti_profile_name": "Agent",
         "cti_profile_enabled": "1",
         "username": "moussa",
         "password": "secret"},
    ]

    response = client.put("/users/import", csv)
    entry = response.item['updated']

    assert_that(entry, has_items(has_entries(user_id=entry1['user_id'],
                                             line_id=entry1['line_id'],
                                             extension_id=entry1['extension_id'],
                                             voicemail_id=entry1['voicemail_id'],
                                             cti_profile_id=entry1['cti_profile_id'],
                                             sip_id=entry1['sip_id'],
                                             incall_extension_id=entry1['incall_extension_id']),
                                 has_entries(user_id=entry2['user_id'],
                                             line_id=entry2['line_id'],
                                             extension_id=entry2['extension_id'],
                                             voicemail_id=entry2['voicemail_id'],
                                             cti_profile_id=entry2['cti_profile_id'],
                                             sccp_id=entry2['sccp_id'],
                                             incall_extension_id=entry2['incall_extension_id'])))


@fixtures.user()
@fixtures.sip()
@fixtures.extension()
@fixtures.extension(context=config.INCALL_CONTEXT)
@fixtures.voicemail()
def test_given_resources_not_associated_when_updating_then_resources_associated(user, sip, extension, incall, voicemail):
    csv = [{"uuid": user['uuid'],
            "exten": extension['exten'],
            "context": extension['context'],
            "line_protocol": "sip",
            "sip_username": sip['username'],
            "incall_exten": incall['exten'],
            "incall_context": incall['context'],
            "voicemail_number": voicemail['number'],
            "voicemail_context": voicemail['context'],
            "cti_profile_name": "Client",
            }]

    response = client.put("/users/import", csv)

    entry = response.item['updated'][0]

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


@fixtures.csv_entry(extension=True, voicemail=True, incall=True, cti_profile=True, line_protocol="sip")
def test_given_each_field_updated_individually_then_entry_updated(entry):
    exten = h.extension.find_available_exten(config.CONTEXT)
    incall_exten = h.extension.find_available_exten(config.INCALL_CONTEXT)
    vm_number = h.voicemail.find_available_number(config.CONTEXT)

    fields = {"entity_id": "1",
              "exten": exten,
              "context": config.CONTEXT,
              "firstname": "Fàbien",
              "lastname": "Bâptiste",
              "email": "fabien@baptiste.st",
              "mobile_phone_number": "5551234567",
              "ring_seconds": "15",
              "simultaneous_calls": "10",
              "language": "fr_FR",
              "outgoing_caller_id": '"Fàbien Le Grand" <5557654321>',
              "userfield": "userfield",
              "supervision_enabled": "1",
              "call_transfer_enabled": "1",
              "sip_username": "fabiensipusername",
              "sip_password": "fabiensippassword",
              "incall_exten": incall_exten,
              "incall_context": config.INCALL_CONTEXT,
              "incall_ring_seconds": "10",
              "voicemail_name": "fabien",
              "voicemail_number": vm_number,
              "voicemail_context": config.CONTEXT,
              "voicemail_password": "1234",
              "voicemail_email": "test@example.com",
              "voicemail_attach_audio": "1",
              "voicemail_delete_messages": "1",
              "voicemail_ask_password": "1",
              "cti_profile_name": "Agent",
              "cti_profile_enabled": "1",
              "username": "fabien",
              "password": "secret"}

    for name, value in fields.iteritems():
        yield update_csv_field, entry['user_uuid'], name, value


def update_csv_field(uuid, field, value):
    csv = [{'uuid': uuid, field: value}]
    response = client.put("/users/import", csv)
    response.assert_ok()
