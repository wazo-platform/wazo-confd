# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from test_api import errors as e
from test_api import associations as a
from test_api import confd
from test_api import fixtures

from hamcrest import assert_that, has_entries, has_items
FAKE_ID = 999999999


def test_get_users_associated_to_voicemail_when_voicemail_does_not_exist():
    response = confd.voicemails(FAKE_ID).users.get()
    response.assert_match(404, e.not_found('Voicemail'))


@fixtures.user()
@fixtures.user()
@fixtures.voicemail()
def test_get_multiple_users_associated_to_voicemail(user1, user2, voicemail):
    expected = has_items(
        has_entries({'user_id': user1['id'],
                     'voicemail_id': voicemail['id']}),
        has_entries({'user_id': user2['id'],
                     'voicemail_id': voicemail['id']}))

    with a.user_voicemail(user1, voicemail), a.user_voicemail(user2, voicemail):
        response = confd.voicemails(voicemail['id']).users.get()
        assert_that(response.items, expected)
