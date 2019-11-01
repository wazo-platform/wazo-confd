# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    contains_string,
    empty,
    equal_to,
    has_entries,
    has_items,
    has_key,
    has_length,
    instance_of,
    is_not,
    not_none,
)

from ..helpers import associations as a, config, fixtures, helpers as h
from . import confd, auth


client = h.user_import.csv_client()


def get_import_field(response, fieldname, row_number=1):
    rows = response.item['created']
    return get_field(rows, fieldname, row_number)


def get_update_field(response, fieldname, row_number=1):
    rows = response.item['updated']
    return get_field(rows, fieldname, row_number)


def get_field(rows, fieldname, row_number=1):
    assert_that(rows, has_length(row_number), "CSV import did not create enough rows")

    row = rows[row_number - 1]
    assert_that(row, has_entries({'row_number': row_number, fieldname: not_none()}))

    return row[fieldname]


def assert_error(response, expect):
    response.assert_status(400)
    assert_that(response.json, has_entries(errors=expect))


def has_error_field(fieldname, row_number=1):
    return contains(
        has_entries(
            timestamp=instance_of(int),
            details=has_entries(row_number=row_number),
            message=contains_string(fieldname),
        )
    )


def test_given_required_fields_missing_then_error_returned():
    csv = [{"lastname": "missingfirstname"}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field("firstname"))


def test_given_csv_has_minimal_fields_for_a_user_then_user_imported():
    csv = [{"firstname": "Rîchard"}]

    response = client.post("/users/import", csv)
    user_id = get_import_field(response, 'user_id')
    user_uuid = get_import_field(response, 'user_uuid')

    user = confd.users(user_id).get().item
    assert_that(user, has_entries(firstname="Rîchard", uuid=user_uuid))


def test_given_csv_has_all_fields_for_a_user_then_user_imported():
    csv = [
        {
            "firstname": "Rîchard",
            "lastname": "Lâpointe",
            "email": "richard@lapointe.org",
            "language": "fr_FR",
            "outgoing_caller_id": '"Rîchy Cool" <4185551234>',
            "mobile_phone_number": "4181234567",
            "supervision_enabled": "1",
            "call_transfer_enabled": "0",
            "dtmf_hangup_enabled": "1",
            "call_record_enabled": "1",
            "online_call_record_enabled": "0",
            "simultaneous_calls": "5",
            "ring_seconds": "10",
            "userfield": "userfield",
            "call_permission_password": "1234",
            "enabled": "1",
            "username": "richardlapointe",
            "password": "secret",
        }
    ]

    response = client.post("/users/import", csv)
    user_id = get_import_field(response, 'user_id')
    user_uuid = get_import_field(response, 'user_uuid')

    user = confd.users(user_id).get().item
    assert_that(
        user,
        has_entries(
            firstname="Rîchard",
            lastname="Lâpointe",
            email="richard@lapointe.org",
            language="fr_FR",
            outgoing_caller_id='"Rîchy Cool" <4185551234>',
            mobile_phone_number="4181234567",
            supervision_enabled=True,
            call_transfer_enabled=False,
            dtmf_hangup_enabled=True,
            call_record_enabled=True,
            online_call_record_enabled=False,
            simultaneous_calls=5,
            ring_seconds=10,
            userfield="userfield",
            call_permission_password='1234',
            enabled=True,
            uuid=user_uuid,
            username=None,
            password=None,
        ),
    )


@fixtures.call_permission()
def test_given_csv_has_all_fields_for_a_user_then_resources_are_in_the_same_tenant(
    call_permission,
):
    number = h.voicemail.find_available_number(config.CONTEXT)
    exten = h.extension.find_available_exten(config.CONTEXT)
    incall_exten = h.extension.find_available_exten(config.INCALL_CONTEXT)
    csv = [
        {
            "firstname": "Bobby",
            "voicemail_name": "Bobby VM",
            "voicemail_number": number,
            "voicemail_context": config.CONTEXT,
            "exten": exten,
            "context": config.CONTEXT,
            "line_protocol": "sip",
            "incall_exten": incall_exten,
            "incall_context": config.INCALL_CONTEXT,
            "call_permissions": call_permission['name'],
        }
    ]

    response = client.post("/users/import", csv)
    entry = response.item['created'][0]

    user = confd.users(entry['user_uuid']).get().item
    assert_that(user, has_entries(tenant_uuid=config.MAIN_TENANT))

    line = confd.lines(entry['line_id']).get().item
    assert_that(line, has_entries(tenant_uuid=config.MAIN_TENANT))

    voicemail = confd.voicemails(entry['voicemail_id']).get().item
    assert_that(voicemail, has_entries(tenant_uuid=config.MAIN_TENANT))

    extension = confd.extensions(entry['extension_id']).get().item
    assert_that(extension, has_entries(tenant_uuid=config.MAIN_TENANT))

    sip_endpoint = confd.endpoints.sip(entry['sip_id']).get().item
    assert_that(sip_endpoint, has_entries(tenant_uuid=config.MAIN_TENANT))

    incall_extension = confd.extensions(entry['incall_extension_id']).get().item
    assert_that(incall_extension, has_entries(tenant_uuid=config.MAIN_TENANT))

    for call_permission_id in entry['call_permission_ids']:
        call_permission = confd.callpermissions(call_permission_id).get().item
        assert_that(call_permission, has_entries(tenant_uuid=config.MAIN_TENANT))


def test_given_an_unknown_context_then_error_returned():
    csv = [{'firstname': 'foo', 'context': 'unknowncontext', "line_protocol": "sip"}]

    response = client.post('/users/import', csv)
    assert_error(response, has_error_field('Context was not found'))


@fixtures.context(wazo_tenant=config.SUB_TENANT)
def test_given_context_in_another_tenant_then_error_returned(context):
    csv = [{'firstname': 'foo', 'context': context['name'], "line_protocol": "sip"}]

    response = client.post('/users/import', csv)
    assert_error(response, has_error_field('Context was not found'))


def test_given_csv_column_has_wrong_type_then_error_returned():
    csv = [{'firstname': 'invalidbool', 'supervision_enabled': 'yeah'}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('supervision_enabled'))


def test_given_user_contains_error_then_error_returned():
    csv = [{"firstname": "richard", "mobile_phone_number": "blah"}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('mobile_phone_number'))


def test_given_csv_has_minimal_voicemail_fields_then_voicemail_imported():
    number, context = h.voicemail.generate_number_and_context()
    csv = [
        {
            "firstname": "Jôey",
            "voicemail_name": "Jôey VM",
            "voicemail_number": number,
            "voicemail_context": context,
        }
    ]

    response = client.post("/users/import", csv)
    voicemail_id = get_import_field(response, 'voicemail_id')

    voicemail = confd.voicemails(voicemail_id).get().item
    assert_that(voicemail, has_entries(name="Jôey VM", number=number, context=context))


def test_given_csv_has_all_voicemail_fields_then_voicemail_imported():
    number, context = h.voicemail.generate_number_and_context()
    csv = [
        {
            "firstname": "Jôey",
            "voicemail_name": "Jôey VM",
            "voicemail_number": number,
            "voicemail_context": context,
            "voicemail_password": "1234",
            "voicemail_email": "email@example.com",
            "voicemail_attach_audio": "0",
            "voicemail_delete_messages": "1",
            "voicemail_ask_password": "0",
        }
    ]

    response = client.post("/users/import", csv)
    voicemail_id = get_import_field(response, 'voicemail_id')

    voicemail = confd.voicemails(voicemail_id).get().item
    assert_that(
        voicemail,
        has_entries(
            name="Jôey VM",
            number=number,
            context=context,
            password="1234",
            email='email@example.com',
            attach_audio=False,
            delete_messages=True,
            ask_password=False,
        ),
    )


def test_given_voicemail_contains_error_then_error_returned():
    csv = [
        {
            "firstname": "Jôey",
            "voicemail_name": "Jôey VM",
            "voicemail_number": "%%%$",
            "voicemail_context": config.CONTEXT,
        }
    ]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('number'))


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(voicemail=True)
def test_update_voicemail_contains_error_then_error_returned(entry):
    csv = [
        {
            "uuid": entry["user_uuid"],
            "voicemail_number": "invalid",
            "voicemail_password": "invalid",
        }
    ]

    response = client.put("/users/import", csv)
    assert_error(response, has_error_field('number'))
    assert_error(response, has_error_field('password'))


def test_given_csv_has_minimal_line_fields_then_line_created():
    csv = [{"firstname": "Chârles", "line_protocol": "sip", "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    line_id = get_import_field(response, 'line_id')

    line = confd.lines(line_id).get().item
    assert_that(line, has_entries(context=config.CONTEXT, protocol='sip'))


def test_given_line_has_error_then_error_returned():
    csv = [
        {"firstname": "Chârles", "line_protocol": "sip", "context": 'invalidcontext'}
    ]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('context'))


def test_given_csv_has_minimal_sip_fields_then_sip_endpoint_created():
    csv = [{"firstname": "Chârles", "line_protocol": "sip", "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    sip_id = get_import_field(response, 'sip_id')

    sip = confd.endpoints.sip(sip_id).get().item
    assert_that(sip, has_entries(id=sip_id))


def test_given_csv_has_none_sip_fields_then_sip_endpoint_created():
    csv = [
        {
            "firstname": "Chârles",
            "line_protocol": "sip",
            "context": config.CONTEXT,
            "sip_username": '',
            "sip_secret": '',
        }
    ]

    response = client.post("/users/import", csv)
    sip_id = get_import_field(response, 'sip_id')

    sip = confd.endpoints.sip(sip_id).get().item
    assert_that(sip, has_entries(id=sip_id))


def test_given_csv_has_all_sip_fields_then_sip_endpoint_created():
    csv = [
        {
            "firstname": "Chârles",
            "line_protocol": "sip",
            "context": config.CONTEXT,
            "sip_username": "sipusername",
            "sip_secret": "sipsecret",
        }
    ]

    response = client.post("/users/import", csv)
    sip_id = get_import_field(response, 'sip_id')

    sip = confd.endpoints.sip(sip_id).get().item
    assert_that(sip, has_entries(username="sipusername", secret="sipsecret"))


def test_given_csv_has_sip_error_then_error_raised():
    csv = [
        {
            "firstname": "Chârles",
            "line_protocol": "sip",
            "context": config.CONTEXT,
            "sip_username": "invalid^^",
            "sip_secret": "\xe0",
        }
    ]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('username'))
    assert_error(response, has_error_field('secret'))


def test_given_csv_has_minimal_sccp_fields_then_sccp_endpoint_created():
    csv = [{"firstname": "Chârles", "line_protocol": "sccp", "context": config.CONTEXT}]

    response = client.post("/users/import", csv)
    sccp_id = get_import_field(response, 'sccp_id')

    sccp = confd.endpoints.sccp(sccp_id).get().item
    assert_that(sccp, has_entries(id=sccp_id))


def test_given_csv_has_extension_fields_then_extension_created():
    exten = h.extension.find_available_exten(config.CONTEXT)
    csv = [
        {
            "firstname": "Géorge",
            "line_protocol": "sip",
            "exten": exten,
            "context": config.CONTEXT,
        }
    ]

    response = client.post("/users/import", csv)
    extension_id = get_import_field(response, 'extension_id')

    extension = confd.extensions(extension_id).get().item
    assert_that(extension, has_entries(exten=exten, context=config.CONTEXT))


def test_given_csv_extension_has_errors_then_errors_returned():
    csv = [
        {
            "firstname": "Géorge",
            "line_protocol": "sip",
            "exten": "9999",
            "context": "invalid",
        }
    ]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('Context was not found'))


def test_given_csv_has_minimal_incall_fields_then_incall_created():
    exten = h.extension.find_available_exten(config.INCALL_CONTEXT)
    csv = [
        {
            "firstname": "Pâscal",
            "line_protocol": "sccp",
            "context": config.CONTEXT,
            "incall_exten": exten,
            "incall_context": config.INCALL_CONTEXT,
        }
    ]

    response = client.post("/users/import", csv)
    extension_incall_id = get_import_field(response, 'incall_extension_id')

    extension = confd.extensions(extension_incall_id).get().item
    assert_that(extension, has_entries(exten=exten, context=config.INCALL_CONTEXT))


def test_given_csv_has_all_incall_fields_then_incall_created():
    exten = h.extension.find_available_exten(config.INCALL_CONTEXT)
    csv = [
        {
            "firstname": "Pâscal",
            "line_protocol": "sccp",
            "context": config.CONTEXT,
            "incall_exten": exten,
            "incall_context": config.INCALL_CONTEXT,
            "incall_ring_seconds": "10",
        }
    ]

    response = client.post("/users/import", csv)
    get_import_field(response, 'incall_extension_id')


def test_given_csv_incall_has_errors_then_errors_returned():
    csv = [
        {
            "firstname": "Géorge",
            "line_protocol": "sip",
            "context": config.CONTEXT,
            "incall_exten": "9999",
            "incall_context": "invalid",
        }
    ]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('context'))


@fixtures.context(type='incall', wazo_tenant=config.SUB_TENANT)
def test_given_csv_incall_in_other_context_then_errors_returned(incall):
    csv = [
        {
            "firstname": "Géorge",
            "incall_exten": "9999",
            "incall_context": incall['name'],
        }
    ]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('context'))


def test_given_csv_has_wazo_user_fields_then_wazo_user_created():
    csv = [
        {
            "firstname": "Thômas",
            "lastname": "dakin",
            "username": "thomas1",
            "password": "secret",
            "email": "thom.dak@user-import.com",
        }
    ]

    response = client.post("/users/import", csv)
    user_uuid = get_import_field(response, 'user_uuid')

    wazo_user = auth.users.get(user_uuid)
    assert_that(
        wazo_user,
        has_entries(
            uuid=user_uuid,
            firstname="Thômas",
            lastname="dakin",
            username="thomas1",
            emails=contains(has_entries(address="thom.dak@user-import.com")),
        ),
    )


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry()
def test_update_wazo_user_fields_then_wazo_user_updated(entry):
    user_uuid = entry["user_uuid"]
    csv = [
        {
            "uuid": user_uuid,
            "firstname": "user-import",
            "lastname": "user-import",
            "username": "user-import",
            "email": "user-import@user-import.com",
            "password": "user-import",
        }
    ]

    response = client.put("/users/import", csv)
    response.assert_ok()

    wazo_user = auth.users.get(user_uuid)
    assert_that(
        wazo_user,
        has_entries(
            uuid=user_uuid,
            firstname="user-import",
            lastname="user-import",
            username="user-import",
            emails=contains(has_entries(address="user-import@user-import.com")),
        ),
    )


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry()
@fixtures.csv_entry()
def test_update_wazo_auth_is_resynchronise_after_error_and_update(entry1, entry2):
    user_uuid = entry1["user_uuid"]
    csv = [
        {"uuid": user_uuid, "firstname": "user-import"},
        {"uuid": entry2['user_uuid'], "firstname": ""},
    ]

    response = client.put("/users/import", csv)
    assert_error(response, has_error_field('firstname', row_number=2))

    wazo_user = auth.users.get(user_uuid)
    assert_that(wazo_user, has_entries(uuid=user_uuid, firstname="user-import"))

    response = confd.users(user_uuid).get()
    assert_that(response.item, has_entries(firstname=entry1['firstname']))

    csv = [
        {"uuid": user_uuid, "firstname": "user-import"},
        {"uuid": entry2['user_uuid'], "firstname": "valid"},
    ]

    response = client.put("/users/import", csv)
    response.assert_ok()

    wazo_user = auth.users.get(user_uuid)
    assert_that(wazo_user, has_entries(uuid=user_uuid, firstname="user-import"))

    response = confd.users(user_uuid).get()
    assert_that(response.item, has_entries(firstname="user-import"))


def test_given_csv_has_error_then_wazo_user_deleted():
    unique_firstname = uuid.uuid4()
    csv = [
        {"firstname": unique_firstname, 'lastname': ""},
        {"firstname": "", 'lastname': ""},
    ]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('firstname', row_number=2))

    wazo_user = auth.users.list()
    assert_that(
        wazo_user['items'], is_not(has_items(has_entries(firstname=unique_firstname)))
    )


@fixtures.call_permission()
def test_given_csv_has_call_permission_then_call_permission_associated(call_permission):
    csv = [{"firstname": "Gërtrüde", "call_permissions": call_permission['name']}]

    response = client.post("/users/import", csv)
    assert_that(
        response.item['created'],
        contains(
            has_entries(
                row_number=1, call_permission_ids=contains(call_permission['id'])
            )
        ),
    )

    user_id = response.item['created'][0]['user_id']
    user_call_permissions = confd.users(user_id).callpermissions.get().items
    assert_that(
        user_call_permissions,
        contains(
            has_entries(call_permission_id=call_permission['id'], user_id=user_id)
        ),
    )


@fixtures.call_permission()
@fixtures.call_permission()
def test_given_csv_has_multiple_call_permissions_then_all_call_permission_associated(
    perm1, perm2
):
    permissions = "{perm1[name]};{perm2[name]}".format(perm1=perm1, perm2=perm2)
    csv = [{"firstname": "Rônald", "call_permissions": permissions}]

    response = client.post("/users/import", csv)
    assert_that(
        response.item['created'],
        contains(
            has_entries(
                row_number=1, call_permission_ids=has_items(perm1['id'], perm2['id'])
            )
        ),
    )

    user_id = response.item['created'][0]['user_id']
    user_call_permissions = confd.users(user_id).callpermissions.get().items
    assert_that(
        user_call_permissions,
        contains_inanyorder(
            has_entries(call_permission_id=perm1['id'], user_id=user_id),
            has_entries(call_permission_id=perm2['id'], user_id=user_id),
        ),
    )


def test_given_call_permission_does_not_exist_then_error_raised():
    csv = [{"firstname": "Trévor", "call_permissions": "unknownperm"}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('CallPermission'))


@fixtures.call_permission(wazo_tenant=config.SUB_TENANT)
def test_given_call_permission_in_other_tenant_then_error_raised(permission):
    csv = [{"firstname": "Trévor", "call_permissions": permission['name']}]

    response = client.post("/users/import", csv)
    assert_error(response, has_error_field('CallPermission'))


def test_given_csv_has_all_resources_then_all_relations_created():
    exten = h.extension.find_available_exten(config.CONTEXT)
    incall_exten = h.extension.find_available_exten(config.INCALL_CONTEXT)
    vm_number = h.voicemail.find_available_number(config.CONTEXT)

    csv = [
        {
            "firstname": "Frânçois",
            "exten": exten,
            "context": config.CONTEXT,
            "line_protocol": "sip",
            "incall_exten": incall_exten,
            "incall_context": config.INCALL_CONTEXT,
            "voicemail_name": "francois",
            "voicemail_number": vm_number,
            "voicemail_context": config.CONTEXT,
        }
    ]

    response = client.post("/users/import", csv)

    user_id = get_import_field(response, 'user_id')
    line_id = get_import_field(response, 'line_id')
    voicemail_id = get_import_field(response, 'voicemail_id')
    extension_id = get_import_field(response, 'extension_id')
    extension_incall_id = get_import_field(response, 'incall_extension_id')
    sip_id = get_import_field(response, 'sip_id')

    response = confd.users(user_id).lines.get()
    assert_that(response.items, contains(has_entries(line_id=line_id)))

    response = confd.lines(line_id).extensions.get()
    assert_that(response.items, has_items(has_entries(extension_id=extension_id)))

    response = confd.extensions(extension_incall_id).get()
    assert_that(response.item['incall'], has_key('id'))

    response = confd.users(user_id).voicemail.get()
    assert_that(response.item, has_entries(voicemail_id=voicemail_id))

    response = confd.lines(line_id).endpoints.sip.get()
    assert_that(response.item, has_entries(endpoint='sip', endpoint_id=sip_id))


@fixtures.sip()
@fixtures.extension()
@fixtures.extension(context=config.INCALL_CONTEXT)
@fixtures.voicemail()
@fixtures.call_permission()
def test_given_resources_already_exist_when_importing_then_resources_associated(
    sip, extension, extension_incall, voicemail, call_permission
):
    csv = [
        {
            "firstname": "importassociate",
            "exten": extension['exten'],
            "context": extension['context'],
            "line_protocol": "sip",
            "sip_username": sip['username'],
            "incall_exten": extension_incall['exten'],
            "incall_context": extension_incall['context'],
            "voicemail_number": voicemail['number'],
            "voicemail_context": voicemail['context'],
            "call_permissions": call_permission['name'],
        }
    ]

    response = client.post("/users/import", csv)

    user_id = get_import_field(response, 'user_id')
    line_id = get_import_field(response, 'line_id')
    extension_incall_id = get_import_field(response, 'incall_extension_id')

    response = confd.users(user_id).lines.get()
    assert_that(response.items, contains(has_entries(line_id=line_id)))

    response = confd.lines(line_id).extensions.get()
    assert_that(response.items, has_items(has_entries(extension_id=extension['id'])))

    response = confd.extensions(extension_incall_id).get()
    assert_that(response.item['incall'], has_key('id'))

    response = confd.users(user_id).voicemail.get()
    assert_that(response.item, has_entries(voicemail_id=voicemail['id']))

    response = confd.lines(line_id).endpoints.sip.get()
    assert_that(response.item, has_entries(endpoint='sip', endpoint_id=sip['id']))

    response = confd.users(user_id).callpermissions.get()
    assert_that(
        response.items,
        contains(
            has_entries(call_permission_id=call_permission['id'], user_id=user_id)
        ),
    )


@fixtures.call_permission()
@fixtures.call_permission()
def test_given_csv_has_more_than_one_entry_then_all_entries_imported(perm1, perm2):
    exten1 = h.extension.find_available_exten(config.CONTEXT)
    incall_exten1 = h.extension.find_available_exten('from-extern')
    vm_number1 = h.voicemail.find_available_number(config.CONTEXT)

    exten2 = h.extension.find_available_exten(config.CONTEXT, exclude=[exten1])
    incall_exten2 = h.extension.find_available_exten(
        'from-extern', exclude=[incall_exten1]
    )
    vm_number2 = h.voicemail.find_available_number(config.CONTEXT, exclude=[vm_number1])

    csv = [
        {
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
            "dtmf_hangup_enabled": "0",
            "call_record_enabled": "0",
            "online_call_record_enabled": "0",
            "call_permission_password": "1234",
            "enabled": "1",
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
            "username": "jean",
            "password": "secret",
            "call_permissions": perm1['name'],
        },
        {
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
            "dtmf_hangup_enabled": "0",
            "call_record_enabled": "1",
            "online_call_record_enabled": "1",
            "call_permission_password": "5678",
            "enabled": "0",
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
            "username": "moussa2",
            "password": "secret",
            "call_permissions": perm2['name'],
        },
    ]

    response = client.post("/users/import", csv)

    assert_that(len(response.item['created']), equal_to(2))


def test_given_field_group_is_empty_then_resource_is_not_created():
    group = {
        "voicemail_name": "",
        "voicemail_number": "",
        "voicemail_context": "",
        "voicemail_password": "",
        "voicemail_email": "",
        "voicemail_attach_audio": "",
        "voicemail_delete_messages": "",
        "voicemail_ask_password": "",
    }
    yield import_empty_group, group, 'voicemail_id'

    group = {"line_protocol": ""}
    yield import_empty_group, group, 'line_id'

    group = {"line_protocol": "sip", "exten": "", "context": ""}
    yield import_empty_group, group, 'extension_id'

    exten = h.extension.find_available_exten(config.CONTEXT)
    group = {
        "line_protocol": "sip",
        "exten": exten,
        "context": config.CONTEXT,
        "incall_exten": "",
        "incall_context": "",
    }
    yield import_empty_group, group, 'incall_extension_id'

    group = {"call_permissions": ""}
    yield import_empty_group, group, 'call_permission_ids', []


def import_empty_group(fields, parameter, expected=None):
    fields['firstname'] = "Abigaël"
    response = client.post("/users/import", [fields])
    entry = response.item['created'][0]
    assert_that(entry, has_entries({parameter: expected}))


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry()
def test_when_updating_user_fields_then_user_resource_updated(entry):
    csv = [
        {
            "uuid": entry['user_uuid'],
            "firstname": "Joël",
            "lastname": "Làchance",
            "language": "fr_FR",
            "email": "joel@lachance.fr",
            "outgoing_caller_id": '"Joël Spîffy" <4185551234>',
            "mobile_phone_number": "4181234567",
            "supervision_enabled": "1",
            "call_transfer_enabled": "0",
            "dtmf_hangup_enabled": "1",
            "call_record_enabled": "1",
            "online_call_record_enabled": "0",
            "simultaneous_calls": "5",
            "ring_seconds": "10",
            "userfield": "userfield",
            "call_permission_password": "123",
            "enabled": "0",
            "username": "joellachance",
            "password": "secret",
        }
    ]

    response = client.put("/users/import", csv)
    user_id = get_update_field(response, 'user_id')
    user_uuid = get_update_field(response, 'user_uuid')

    user = confd.users(user_id).get().item
    assert_that(
        user,
        has_entries(
            firstname="Joël",
            lastname="Làchance",
            email="joel@lachance.fr",
            language="fr_FR",
            outgoing_caller_id='"Joël Spîffy" <4185551234>',
            mobile_phone_number="4181234567",
            supervision_enabled=True,
            call_transfer_enabled=False,
            dtmf_hangup_enabled=True,
            call_record_enabled=True,
            online_call_record_enabled=False,
            simultaneous_calls=5,
            ring_seconds=10,
            userfield="userfield",
            call_permission_password='123',
            enabled=False,
            uuid=user_uuid,
            username=None,
            password=None,
        ),
    )


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(voicemail=True)
def test_when_updating_voicemail_fields_then_voicemail_updated(entry):
    number = h.voicemail.find_available_number(config.CONTEXT)

    csv = [
        {
            "uuid": entry["user_uuid"],
            "voicemail_name": "Jôey VM",
            "voicemail_number": number,
            "voicemail_context": config.CONTEXT,
            "voicemail_password": "1234",
            "voicemail_email": "email@example.com",
            "voicemail_attach_audio": "0",
            "voicemail_delete_messages": "1",
            "voicemail_ask_password": "0",
        }
    ]

    response = client.put("/users/import", csv)
    voicemail_id = get_update_field(response, 'voicemail_id')

    voicemail = confd.voicemails(voicemail_id).get().item
    assert_that(
        voicemail,
        has_entries(
            name="Jôey VM",
            number=number,
            context=config.CONTEXT,
            password="1234",
            email='email@example.com',
            attach_audio=False,
            delete_messages=True,
            ask_password=False,
        ),
    )


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry()
def test_when_adding_voicemail_fields_then_voicemail_created(entry):
    number = h.voicemail.find_available_number(config.CONTEXT)

    csv = [
        {
            "uuid": entry['user_uuid'],
            "voicemail_name": "Jôey VM",
            "voicemail_number": number,
            "voicemail_context": config.CONTEXT,
            "voicemail_password": "1234",
            "voicemail_email": "email@example.com",
            "voicemail_attach_audio": "0",
            "voicemail_delete_messages": "1",
            "voicemail_ask_password": "0",
        }
    ]

    response = client.put("/users/import", csv)
    voicemail_id = get_update_field(response, 'voicemail_id')

    voicemail = confd.voicemails(voicemail_id).get().item
    assert_that(
        voicemail,
        has_entries(
            name="Jôey VM",
            number=number,
            context=config.CONTEXT,
            password="1234",
            email='email@example.com',
            attach_audio=False,
            delete_messages=True,
            ask_password=False,
        ),
    )


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(line_protocol="sip")
def test_when_updating_sip_line_fields_then_sip_updated(entry):
    csv = [
        {
            "uuid": entry["user_uuid"],
            "sip_username": "mynewsipusername",
            "sip_secret": "mynewsippassword",
        }
    ]

    response = client.put("/users/import", csv)
    sip_id = get_update_field(response, 'sip_id')

    sip = confd.endpoints.sip(sip_id).get().item
    assert_that(
        sip, has_entries(username="mynewsipusername", secret="mynewsippassword")
    )


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(line_protocol="sip")
def test_when_updating_sip_line_fields_to_none_then_error_raised(entry):
    csv = [{"uuid": entry["user_uuid"], "sip_username": "", "sip_secret": ""}]

    response = client.put("/users/import", csv)
    assert_error(response, has_error_field('username'))
    assert_error(response, has_error_field('secret'))


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry()
def test_when_adding_sip_line_then_sip_created(entry):
    csv = [
        {
            "uuid": entry["user_uuid"],
            "line_protocol": "sip",
            "sip_username": "createdsipusername",
            "sip_secret": "createdsippassword",
        }
    ]

    response = client.put("/users/import", csv)
    sip_id = get_update_field(response, 'sip_id')

    sip = confd.endpoints.sip(sip_id).get().item
    assert_that(
        sip, has_entries(username="createdsipusername", secret="createdsippassword")
    )


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry()
def test_when_adding_sccp_line_then_sccp_created(entry):
    csv = [{"uuid": entry["user_uuid"], "line_protocol": "sccp"}]

    response = client.put("/users/import", csv)
    sccp_id = get_update_field(response, 'sccp_id')

    sccp = confd.endpoints.sccp(sccp_id).get().item
    assert_that(sccp, has_entries(id=sccp_id))


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(line_protocol="sip")
def test_when_changing_line_protocol_then_error_raised(entry):
    csv = [{"uuid": entry["user_uuid"], "line_protocol": "sccp"}]

    response = client.put("/users/import", csv)

    assert_error(response, has_error_field('endpoint'))


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(extension=True)
def test_when_updating_extension_then_extension_updated(entry):
    exten = h.extension.find_available_exten(config.CONTEXT)

    csv = [{"uuid": entry["user_uuid"], "exten": exten, "context": config.CONTEXT}]

    response = client.put("/users/import", csv)
    extension_id = get_update_field(response, 'extension_id')

    extension = confd.extensions(extension_id).get().item
    assert_that(extension, has_entries(exten=exten, context=config.CONTEXT))


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(extension=True)
@fixtures.line_sip()
@fixtures.extension()
def test_when_updating_extension_then_only_main_extension_updated(
    entry, line2, extension2
):
    exten = h.extension.find_available_exten(config.CONTEXT)

    user = {'id': entry['user_uuid']}
    with a.user_line(user, line2), a.line_extension(line2, extension2):
        csv = [{"uuid": entry["user_uuid"], "exten": exten, "context": config.CONTEXT}]

        response = client.put("/users/import", csv)
        extension_id = get_update_field(response, 'extension_id')

        response = confd.extensions(extension_id).get().item
        assert_that(response, has_entries(exten=exten, context=config.CONTEXT))

        response = confd.extensions(extension2['id']).get().item
        assert_that(response, has_entries(exten=extension2['exten']))


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(line_protocol="sip")
def test_when_adding_extension_then_extension_created(entry):
    exten = h.extension.find_available_exten(config.CONTEXT)

    csv = [{"uuid": entry["user_uuid"], "exten": exten, "context": config.CONTEXT}]

    response = client.put("/users/import", csv)
    extension_id = get_update_field(response, 'extension_id')

    extension = confd.extensions(extension_id).get().item
    assert_that(extension, has_entries(exten=exten, context=config.CONTEXT))


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(incall=True)
def test_when_updating_incall_fields_then_incall_updated(entry):
    exten = h.extension.find_available_exten(config.INCALL_CONTEXT)

    csv = [
        {
            "uuid": entry["user_uuid"],
            "incall_exten": exten,
            "incall_context": config.INCALL_CONTEXT,
            "incall_ring_seconds": "10",
        }
    ]

    response = client.put("/users/import", csv)
    extension_incall_id = get_update_field(response, 'incall_extension_id')

    extension = confd.extensions(extension_incall_id).get().item
    assert_that(extension, has_entries(exten=exten, context=config.INCALL_CONTEXT))


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(line_protocol="sip", extension=True)
def test_when_adding_incall_then_incall_created(entry):
    exten = h.extension.find_available_exten(config.INCALL_CONTEXT)

    csv = [
        {
            "uuid": entry["user_uuid"],
            "incall_exten": exten,
            "incall_context": config.INCALL_CONTEXT,
            "incall_ring_seconds": "10",
        }
    ]

    response = client.put("/users/import", csv)
    extension_incall_id = get_update_field(response, 'incall_extension_id')

    extension = confd.extensions(extension_incall_id).get().item
    assert_that(extension, has_entries(exten=exten, context=config.INCALL_CONTEXT))


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(call_permissions=2)
@fixtures.call_permission()
@fixtures.call_permission()
def test_when_updating_call_permission_field_then_call_permissions_updated(
    entry, perm1, perm2
):
    permissions = "{perm1[name]};{perm2[name]}".format(perm1=perm1, perm2=perm2)
    csv = [{"uuid": entry['user_uuid'], "call_permissions": permissions}]

    response = client.put("/users/import", csv)

    assert_that(
        response.item['updated'],
        contains(
            has_entries(
                row_number=1, call_permission_ids=has_items(perm1['id'], perm2['id'])
            )
        ),
    )

    old_perm_id1, old_perm_id2 = entry['call_permission_ids']
    user_id = response.item['updated'][0]['user_id']

    response = confd.users(user_id).callpermissions.get()
    assert_that(
        response.items,
        contains_inanyorder(
            has_entries(call_permission_id=perm1['id'], user_id=user_id),
            has_entries(call_permission_id=perm2['id'], user_id=user_id),
        ),
    )


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(call_permissions=1)
def test_when_call_permission_column_is_empty_then_call_permission_is_removed(entry):
    csv = [{"uuid": entry['user_uuid'], "call_permissions": ""}]

    response = client.put("/users/import", csv)

    assert_that(
        response.item['updated'],
        contains(has_entries(row_number=1, call_permission_ids=empty())),
    )

    user_id = response.item['updated'][0]['user_id']

    response = confd.users(user_id).callpermissions.get()
    assert_that(response.items, empty())


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(call_permissions=1)
def test_when_call_permission_column_is_not_in_csv_then_call_permission_remains_unchanged(
    entry,
):
    csv = [{"uuid": entry['user_uuid']}]

    perm_id = entry['call_permission_ids'][0]

    response = client.put("/users/import", csv)

    assert_that(
        response.item['updated'],
        contains(has_entries(row_number=1, call_permission_ids=contains(perm_id))),
    )


def check_error_on_update(entry, fields, error):
    entry = dict(entry)
    entry.update(fields)
    entry['uuid'] = entry['user_uuid']
    response = client.put("/users/import", [entry])
    assert_error(response, has_error_field(error))


@unittest.skip('PUT has been disabled')
def test_given_csv_has_errors_then_errors_returned():
    with fixtures.csv_entry(voicemail=True, incall=True, line_protocol="sip") as entry:
        yield check_error_on_update, entry, {'firstname': ''}, 'firstname'
        yield check_error_on_update, entry, {'voicemail_number': '^]'}, 'number'
        yield check_error_on_update, entry, {'sip_username': '^]'}, 'name'


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(extension=True, voicemail=True, incall=True, line_protocol="sip")
@fixtures.csv_entry(extension=True, voicemail=True, incall=True, line_protocol="sccp")
def test_given_2_entries_in_csv_then_2_entries_updated(entry1, entry2):
    exten1 = h.extension.find_available_exten(config.CONTEXT)
    incall_exten1 = h.extension.find_available_exten(config.INCALL_CONTEXT)
    vm_number1 = h.voicemail.find_available_number(config.CONTEXT)

    exten2 = h.extension.find_available_exten(config.CONTEXT, exclude=[exten1])
    incall_exten2 = h.extension.find_available_exten(
        config.INCALL_CONTEXT, exclude=[incall_exten1]
    )
    vm_number2 = h.voicemail.find_available_number(config.CONTEXT, exclude=[vm_number1])

    csv = [
        {
            "uuid": entry1["user_uuid"],
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
            "dtmf_hangup_enabled": "0",
            "call_record_enabled": "0",
            "online_call_record_enabled": "0",
            "call_permission_password": "321",
            "enabled": "1",
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
            "username": "george",
            "password": "secret",
        },
        {
            "uuid": entry2['user_uuid'],
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
            "dtmf_hangup_enabled": "0",
            "call_record_enabled": "1",
            "online_call_record_enabled": "1",
            "call_permission_password": "654",
            "enabled": "0",
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
            "username": "moussa1",
            "password": "secret",
        },
    ]

    response = client.put("/users/import", csv)
    entry = response.item['updated']

    assert_that(
        entry,
        has_items(
            has_entries(
                user_id=entry1['user_id'],
                line_id=entry1['line_id'],
                extension_id=entry1['extension_id'],
                voicemail_id=entry1['voicemail_id'],
                sip_id=entry1['sip_id'],
                incall_extension_id=entry1['incall_extension_id'],
            ),
            has_entries(
                user_id=entry2['user_id'],
                line_id=entry2['line_id'],
                extension_id=entry2['extension_id'],
                voicemail_id=entry2['voicemail_id'],
                sccp_id=entry2['sccp_id'],
                incall_extension_id=entry2['incall_extension_id'],
            ),
        ),
    )


@unittest.skip('PUT has been disabled')
@fixtures.user()
@fixtures.sip()
@fixtures.extension()
@fixtures.extension(context=config.INCALL_CONTEXT)
@fixtures.voicemail()
@fixtures.call_permission()
def test_given_resources_not_associated_when_updating_then_resources_associated(
    user, sip, extension, extension_incall, voicemail, call_permission
):
    auth.users.new(uuid=user['uuid'], username=user['uuid'])

    csv = [
        {
            "uuid": user['uuid'],
            "exten": extension['exten'],
            "context": extension['context'],
            "line_protocol": "sip",
            "sip_username": sip['username'],
            "incall_exten": extension_incall['exten'],
            "incall_context": extension_incall['context'],
            "voicemail_number": voicemail['number'],
            "voicemail_context": voicemail['context'],
            "call_permissions": call_permission['name'],
        }
    ]

    response = client.put("/users/import", csv)

    entry = response.item['updated'][0]

    response = confd.users(entry['user_id']).lines.get()
    assert_that(response.items, contains(has_entries(line_id=entry['line_id'])))

    response = confd.lines(entry['line_id']).extensions.get()
    assert_that(
        response.items, has_items(has_entries(extension_id=entry['extension_id']))
    )

    response = confd.extensions(entry['incall_extension_id']).get()
    assert_that(response.item['incall'], has_key('id'))

    response = confd.users(entry['user_id']).voicemail.get()
    assert_that(response.item, has_entries(voicemail_id=entry['voicemail_id']))

    response = confd.lines(entry['line_id']).endpoints.sip.get()
    assert_that(response.item, has_entries(endpoint='sip', endpoint_id=entry['sip_id']))

    response = confd.users(entry['user_id']).callpermissions.get()
    assert_that(
        response.items,
        contains_inanyorder(
            has_entries(
                call_permission_id=call_permission['id'], user_id=entry['user_id']
            )
        ),
    )


@unittest.skip('PUT has been disabled')
@fixtures.csv_entry(
    extension=True, voicemail=True, incall=True, line_protocol="sip", call_permissions=1
)
@fixtures.call_permission()
def test_given_each_field_updated_individually_then_entry_updated(
    entry, call_permission
):
    exten = h.extension.find_available_exten(config.CONTEXT)
    incall_exten = h.extension.find_available_exten(config.INCALL_CONTEXT)
    vm_number = h.voicemail.find_available_number(config.CONTEXT)

    fields = {
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
        "dtmf_hangup_enabled": "0",
        "call_record_enabled": "1",
        "online_call_record_enabled": "1",
        "call_permission_password": "542",
        "enabled": "0",
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
        "username": "fabien",
        "call_permissions": call_permission['name'],
        "password": "secret",
    }

    for name, value in fields.items():
        yield update_csv_field, entry['user_uuid'], name, value


def update_csv_field(uuid, field, value):
    csv = [{'uuid': uuid, field: value}]
    response = client.put("/users/import", csv)
    response.assert_ok()
