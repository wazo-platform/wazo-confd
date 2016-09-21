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

from hamcrest import assert_that, has_item, has_entries

from test_api import confd_csv
from test_api import config
from test_api import fixtures
from test_api import associations as a


@fixtures.user(firstname="Ûrsule",
               lastname="Wèrber",
               email="ursule@werber.com",
               mobile_phone_number="5551234567",
               language="fr_FR",
               outgoing_caller_id="Hûrsule <4441234567>",
               userfield="userfield",
               ring_seconds=15,
               simultaneous_calls=10,
               supervision_enabled=True,
               call_transfer_enabled=False,
               dtmf_hangup_enabled=False,
               call_record_enabled=False,
               online_call_record_enabled=False,
               call_permission_password="1234",
               enabled=True,
               username="ursule",
               password="ursulepassword")
def test_given_user_with_no_associations_when_exporting_then_csv_has_all_user_fields(user):
    expected = has_entries(uuid=user['uuid'],
                           firstname="Ûrsule",
                           lastname="Wèrber",
                           email="ursule@werber.com",
                           mobile_phone_number="5551234567",
                           language="fr_FR",
                           outgoing_caller_id="Hûrsule <4441234567>",
                           userfield="userfield",
                           ring_seconds="15",
                           simultaneous_calls="10",
                           supervision_enabled="1",
                           call_transfer_enabled="0",
                           dtmf_hangup_enabled="0",
                           call_record_enabled="0",
                           online_call_record_enabled="0",
                           call_permission_password="1234",
                           enabled="1",
                           username="ursule",
                           password="ursulepassword",
                           entity_id="1")

    response = confd_csv.users.export.get()
    assert_that(response.csv(), has_item(expected))


@fixtures.user()
@fixtures.voicemail(name="Jàmie",
                    password="1234",
                    email="test@example.com",
                    attach_audio=True,
                    delete_messages=True,
                    ask_password=True)
def test_given_user_has_voicemail_when_exporting_then_csv_has_voicemail_fields(user, voicemail):
    expected = has_entries(uuid=user['uuid'],
                           voicemail_name="Jàmie",
                           voicemail_number=voicemail['number'],
                           voicemail_context=voicemail['context'],
                           voicemail_password="1234",
                           voicemail_email="test@example.com",
                           voicemail_attach_audio="1",
                           voicemail_delete_messages="1",
                           voicemail_ask_password="1")

    with a.user_voicemail(user, voicemail):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(expected))


@fixtures.cti_profile()
@fixtures.user(username="floogle",
               password="secret")
def test_given_user_has_cti_profile_when_exporting_then_csv_has_cti_profile_fields(cti_profile, user):
    expected = has_entries(uuid=user['uuid'],
                           cti_profile_name=cti_profile['name'],
                           cti_profile_enabled="1")

    with a.user_cti_profile(user, cti_profile):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(expected))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
def test_given_user_has_sip_line_when_exporting_then_csv_has_line_fields(user, line, sip):
    expected = has_entries(uuid=user['uuid'],
                           line_protocol="sip",
                           provisioning_code=line['provisioning_code'],
                           context=line['context'],
                           sip_username=sip['username'],
                           sip_secret=sip['secret'])

    with a.line_endpoint_sip(line, sip), a.user_line(user, line):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(expected))


@fixtures.user()
@fixtures.line()
@fixtures.sccp()
def test_given_user_has_sccp_line_when_exporting_then_csv_has_line_fields(user, line, sccp):
    expected = has_entries(uuid=user['uuid'],
                           line_protocol="sccp",
                           context=line['context'])

    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(expected))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_given_user_has_extension_when_exporting_then_csv_has_extension_fields(user, line, sip, extension):
    expected = has_entries(uuid=user['uuid'],
                           exten=extension['exten'],
                           context=extension['context'])

    with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(line, extension):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(expected))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.incall()
@fixtures.extension(context=config.INCALL_CONTEXT)
def test_given_user_has_incall_when_exporting_then_csv_has_incall_fields(user, line, sip, incall, extension):
    expected = has_entries(uuid=user['uuid'],
                           incall_exten=extension['exten'],
                           incall_context=extension['context'])

    with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.incall_extension(incall, extension), a.incall_user(incall, user):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(expected))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.incall()
@fixtures.incall()
@fixtures.extension(context=config.INCALL_CONTEXT)
@fixtures.extension(context=config.INCALL_CONTEXT)
def test_given_user_has_multiple_incalls_when_exporting_then_csv_has_incall_fields(user,
                                                                                   line,
                                                                                   sip,
                                                                                   incall1,
                                                                                   incall2,
                                                                                   extension1,
                                                                                   extension2):
    expected_incall = ";".join([extension1['exten'], extension2['exten']])
    expected_context = ";".join([extension1['context'], extension2['context']])
    expected = has_entries(uuid=user['uuid'],
                           incall_exten=expected_incall,
                           incall_context=expected_context
                           )

    with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.incall_extension(incall1, extension1), a.incall_extension(incall2, extension2), \
            a.incall_user(incall1, user), a.incall_user(incall2, user):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(expected))


@fixtures.user()
@fixtures.call_permission()
@fixtures.call_permission()
def test_given_user_has_multiple_call_permissions_when_exporting_then_csv_has_call_permission_field(user, perm1, perm2):
    permissions = sorted([perm1['name'], perm2['name']])
    expected_permissions = ";".join(permissions)
    expected = has_entries(uuid=user['uuid'],
                           call_permissions=expected_permissions)

    with a.user_call_permission(user, perm1), a.user_call_permission(user, perm2):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(expected))
