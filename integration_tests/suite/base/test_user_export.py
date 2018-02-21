# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (
    assert_that,
    has_entries,
    has_item,
)

from ..helpers import (
    associations as a,
    config,
    fixtures,
)
from . import confd_csv


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
               username="ursule")
def test_given_user_with_no_associations_when_exporting_then_csv_has_all_user_fields(user):
    response = confd_csv.users.export.get()
    assert_that(response.csv(), has_item(has_entries(
        uuid=user['uuid'],
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
        entity_id="1",
    )))


@fixtures.user()
@fixtures.voicemail(name="Jàmie",
                    password="1234",
                    email="test@example.com",
                    attach_audio=True,
                    delete_messages=True,
                    ask_password=True)
def test_given_user_has_voicemail_when_exporting_then_csv_has_voicemail_fields(user, voicemail):
    with a.user_voicemail(user, voicemail):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(has_entries(
            uuid=user['uuid'],
            voicemail_name="Jàmie",
            voicemail_number=voicemail['number'],
            voicemail_context=voicemail['context'],
            voicemail_password="1234",
            voicemail_email="test@example.com",
            voicemail_attach_audio="1",
            voicemail_delete_messages="1",
            voicemail_ask_password="1"
        )))


@fixtures.cti_profile()
@fixtures.user(username="floogle",
               password="secret")
def test_given_user_has_cti_profile_when_exporting_then_csv_has_cti_profile_fields(cti_profile, user):
    with a.user_cti_profile(user, cti_profile):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(has_entries(
            uuid=user['uuid'],
            cti_profile_name=cti_profile['name'],
            cti_profile_enabled="1"
        )))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
def test_given_user_has_sip_line_when_exporting_then_csv_has_line_fields(user, line, sip):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(has_entries(
            uuid=user['uuid'],
            line_protocol="sip",
            provisioning_code=line['provisioning_code'],
            context=line['context'],
            sip_username=sip['username'],
            sip_secret=sip['secret']
        )))


@fixtures.user()
@fixtures.line()
@fixtures.sccp()
def test_given_user_has_sccp_line_when_exporting_then_csv_has_line_fields(user, line, sccp):
    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(has_entries(
            uuid=user['uuid'],
            line_protocol="sccp",
            context=line['context']
        )))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_given_user_has_extension_when_exporting_then_csv_has_extension_fields(user, line, sip, extension):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(line, extension):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(has_entries(
            uuid=user['uuid'],
            exten=extension['exten'],
            context=extension['context']
        )))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.incall()
@fixtures.extension(context=config.INCALL_CONTEXT)
def test_given_user_has_incall_when_exporting_then_csv_has_incall_fields(user, line, sip, incall, extension):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.incall_extension(incall, extension), a.incall_user(incall, user):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(has_entries(
            uuid=user['uuid'],
            incall_exten=extension['exten'],
            incall_context=extension['context']
        )))


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
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.incall_extension(incall1, extension1), a.incall_extension(incall2, extension2), \
            a.incall_user(incall1, user), a.incall_user(incall2, user):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(has_entries(
            uuid=user['uuid'],
            incall_exten=";".join([extension1['exten'], extension2['exten']]),
            incall_context=";".join([extension1['context'], extension2['context']]),
        )))


@fixtures.user()
@fixtures.call_permission()
@fixtures.call_permission()
def test_given_user_has_multiple_call_permissions_when_exporting_then_csv_has_call_permission_field(user, perm1, perm2):
    with a.user_call_permission(user, perm1), a.user_call_permission(user, perm2):
        response = confd_csv.users.export.get()
        assert_that(response.csv(), has_item(has_entries(
            uuid=user['uuid'],
            call_permissions=";".join(sorted([perm1['name'], perm2['name']]))
        )))
