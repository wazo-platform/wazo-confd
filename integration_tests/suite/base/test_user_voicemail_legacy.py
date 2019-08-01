# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from ..helpers import helpers as h
from ..helpers import errors as e
from ..helpers import associations as a
from ..helpers import fixtures
from . import confd

FAKE_ID = 999999999


@fixtures.user()
@fixtures.voicemail()
def test_associate_errors(user, voicemail):
    response = confd.users(FAKE_ID).voicemail.post(voicemail_id=voicemail['id'])
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(user['id']).voicemail.post(voicemail_id=FAKE_ID)
    response.assert_match(400, e.not_found(resource='Voicemail'))


@fixtures.user()
@fixtures.voicemail()
def test_dissociate_errors(user, voicemail):
    fake_user = confd.users(FAKE_ID).voicemail.delete
    s.check_resource_not_found(fake_user, 'User')


@fixtures.user()
def test_get_errors(user):
    fake_user = confd.users(FAKE_ID).voicemail.get
    s.check_resource_not_found(fake_user, 'User')


@fixtures.user()
@fixtures.voicemail()
def test_associate(user, voicemail):
    response = confd.users(user['id']).voicemail.post(voicemail_id=voicemail['id'])
    response.assert_created('users', 'voicemail')


@fixtures.user()
@fixtures.voicemail()
def test_associate_using_uuid(user, voicemail):
    response = confd.users(user['uuid']).voicemail.post(voicemail_id=voicemail['id'])
    response.assert_created('users', 'voicemail')


@fixtures.user()
@fixtures.voicemail()
def test_associate_when_already_associated(user, voicemail):
    with a.user_voicemail(user, voicemail):
        response = confd.users(user['id']).voicemail.post(voicemail_id=voicemail['id'])
        response.assert_ok()


@fixtures.user()
@fixtures.user()
@fixtures.voicemail()
def test_associate_multiple_users_to_voicemail(user1, user2, voicemail):
    response = confd.users(user1['id']).voicemail.post(voicemail_id=voicemail['id'])
    response.assert_created('users', 'voicemail')

    response = confd.users(user2['id']).voicemail.post(voicemail_id=voicemail['id'])
    response.assert_created('users', 'voicemail')


@fixtures.user()
def test_get_when_not_associated(user):
    response = confd.users(user['id']).voicemail.get()
    response.assert_match(404, e.not_found('UserVoicemail'))


@fixtures.user()
@fixtures.voicemail()
def test_get_user_voicemail_association(user, voicemail):
    expected = has_entries({'user_id': user['id'],
                            'voicemail_id': voicemail['id']})

    with a.user_voicemail(user, voicemail):
        response = confd.users(user['id']).voicemail.get()
        assert_that(response.item, expected)

        response = confd.users(user['uuid']).voicemail.get()
        assert_that(response.item, expected)


@fixtures.user()
@fixtures.voicemail()
def test_get_user_voicemail_after_dissociation(user, voicemail):
    h.user_voicemail.associate(user['id'], voicemail['id'])
    h.user_voicemail.dissociate(user['id'], voicemail['id'])

    response = confd.users(user['id']).voicemail.get()
    response.assert_match(404, e.not_found('UserVoicemail'))

    response = confd.users(user['uuid']).voicemail.get()
    response.assert_match(404, e.not_found('UserVoicemail'))


@fixtures.user()
@fixtures.voicemail()
def test_dissociate(user, voicemail):
    with a.user_voicemail(user, voicemail, check=False):
        response = confd.users(user['id']).voicemail.delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.voicemail()
def test_dissociate_using_uuid(user, voicemail):
    with a.user_voicemail(user, voicemail, check=False):
        response = confd.users(user['uuid']).voicemail.delete()
        response.assert_deleted()


@fixtures.user()
def test_dissociate_when_not_associated(user):
    response = confd.users(user['id']).voicemail.delete()
    response.assert_match(404, e.not_found('UserVoicemail'))
