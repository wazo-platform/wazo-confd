# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries, empty
from . import BaseIntegrationTest, confd
from ..helpers import (
    associations as a,
    fixtures,
)
from ..helpers.config import DELETED_TENANT


@fixtures.context(name='DELETED', wazo_tenant=DELETED_TENANT)
@fixtures.user(wazo_tenant=DELETED_TENANT)
@fixtures.voicemail(context='DELETED')
def test_remove_user_with_voicemail(_, user, voicemail):
    with a.user_voicemail(user, voicemail, check=False):
        with BaseIntegrationTest.delete_auth_tenant(DELETED_TENANT):
            BaseIntegrationTest.sync_db()

        response = confd.users(user['uuid']).get()
        response.assert_status(404)

        response = confd.voicemails(voicemail['id']).get()
        assert_that(response.item, has_entries(users=empty()))


@fixtures.context(name='DELETED', wazo_tenant=DELETED_TENANT)
@fixtures.user(wazo_tenant=DELETED_TENANT)
def test_remove_user_with_line(context, user):
    with fixtures.line_sip(context=context, wazo_tenant=DELETED_TENANT) as line:
        with a.user_line(user, line, check=False):
            with BaseIntegrationTest.delete_auth_tenant(DELETED_TENANT):
                BaseIntegrationTest.sync_db()

            response = confd.users(user['uuid']).get()
            response.assert_status(404)

            response = confd.lines(line['id']).get()
            assert_that(response.item, has_entries(users=empty()))
