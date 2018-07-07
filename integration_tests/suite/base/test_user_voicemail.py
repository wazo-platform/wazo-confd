# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains_inanyorder,
    has_entries,
    has_items,
)

from . import confd
from ..helpers import scenarios as s
from ..helpers import helpers as h
from ..helpers import errors as e
from ..helpers import associations as a
from ..helpers import fixtures
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_ID = 999999999


@fixtures.user()
@fixtures.voicemail()
def test_associate_errors(user, voicemail):
    fake_user = confd.users(FAKE_ID).voicemails(voicemail['id']).put
    fake_voicemail = confd.users(user['id']).voicemails(FAKE_ID).put

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_voicemail, 'Voicemail'


@fixtures.user()
@fixtures.voicemail()
def test_dissociate_errors(user, voicemail):
    fake_user = confd.users(FAKE_ID).voicemails.delete

    yield s.check_resource_not_found, fake_user, 'User'


@fixtures.user()
def test_get_errors(user):
    fake_user = confd.users(FAKE_ID).voicemails.get
    fake_voicemail = confd.voicemails(FAKE_ID).users.get

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_voicemail, 'Voicemail'


@fixtures.user()
@fixtures.voicemail()
def test_associate(user, voicemail):
    response = confd.users(user['id']).voicemails(voicemail['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.voicemail()
def test_associate_using_uuid(user, voicemail):
    response = confd.users(user['id']).voicemails(voicemail['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.voicemail()
def test_associate_when_already_associated(user, voicemail):
    with a.user_voicemail(user, voicemail):
        response = confd.users(user['id']).voicemails(voicemail['id']).put()
        response.assert_updated()


@fixtures.user()
@fixtures.user()
@fixtures.voicemail()
def test_associate_multiple_users_to_voicemail(user1, user2, voicemail):
    response = confd.users(user1['id']).voicemails(voicemail['id']).put()
    response.assert_updated()

    response = confd.users(user2['id']).voicemails(voicemail['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.voicemail()
def test_get_user_voicemail_association(user, voicemail):
    expected = has_entries({'user_id': user['id'],
                            'voicemail_id': voicemail['id']})

    with a.user_voicemail(user, voicemail):
        response = confd.users(user['id']).voicemails.get()
        assert_that(response.item, expected)

        response = confd.users(user['uuid']).voicemails.get()
        assert_that(response.item, expected)


@fixtures.user()
@fixtures.voicemail()
def test_get_user_voicemail_after_dissociation(user, voicemail):
    h.user_voicemail.associate(user['id'], voicemail['id'])
    h.user_voicemail.dissociate(user['id'], voicemail['id'])

    response = confd.users(user['id']).voicemails.get()
    response.assert_match(404, e.not_found('UserVoicemail'))

    response = confd.users(user['uuid']).voicemails.get()
    response.assert_match(404, e.not_found('UserVoicemail'))


@fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT)
@fixtures.voicemail(context='main_ctx')
@fixtures.voicemail(context='sub_ctx')
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(_, __, main_vm, sub_vm, main_user, sub_user):
    response = confd.users(main_user['uuid']).voicemails(sub_vm['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('User'))

    response = confd.users(sub_user['uuid']).voicemails(main_vm['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Voicemail'))

    response = confd.users(main_user['uuid']).voicemails(sub_vm['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.user()
@fixtures.voicemail()
def test_dissociate(user, voicemail):
    with a.user_voicemail(user, voicemail, check=False):
        response = confd.users(user['id']).voicemails.delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.voicemail()
def test_dissociate_using_uuid(user, voicemail):
    with a.user_voicemail(user, voicemail, check=False):
        response = confd.users(user['uuid']).voicemails.delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.voicemail()
def test_dissociate_not_associated(user, voicemail):
    response = confd.users(user['id']).voicemails.delete()
    response.assert_deleted()


@fixtures.user(wazo_tenant=MAIN_TENANT)
def test_dissociate_multi_tenant(user):
    response = confd.users(user['uuid']).voicemails.delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('User'))


@fixtures.user()
@fixtures.voicemail()
def test_get_voicemail_relation(user, voicemail):
    with a.user_voicemail(user, voicemail):
        response = confd.users(user['id']).get()
        assert_that(
            response.item,
            has_entries(
                voicemail=has_entries(id=voicemail['id'], name=voicemail['name']),
            )
        )


@fixtures.user()
@fixtures.user()
@fixtures.voicemail()
def test_get_users_relation(u1, u2, voicemail):
    with a.user_voicemail(u1, voicemail), a.user_voicemail(u2, voicemail):
        response = confd.voicemails(voicemail['id']).get()
        assert_that(
            response.item['users'],
            contains_inanyorder(
                has_entries(uuid=u1['uuid'], firstname=u1['firstname'], lastname=u1['lastname']),
                has_entries(uuid=u2['uuid'], firstname=u2['firstname'], lastname=u2['lastname']),
            )
        )


@fixtures.user()
@fixtures.voicemail()
def test_delete_user_when_still_associated(user, voicemail):
    with a.user_voicemail(user, voicemail):
        response = confd.users(user['id']).delete()
        response.assert_match(400, e.resource_associated('User', 'Voicemail'))


@fixtures.user()
@fixtures.voicemail()
def test_delete_voicemail_when_still_associated(user, voicemail):
    with a.user_voicemail(user, voicemail):
        response = confd.voicemails(voicemail['id']).delete()
        response.assert_match(400, e.resource_associated('Voicemail', 'User'))


@fixtures.user()
@fixtures.voicemail()
def test_edit_voicemail_when_still_associated(user, voicemail):
    number = h.voicemail.find_available_number(voicemail['context'])
    with a.user_voicemail(user, voicemail):
        response = confd.voicemails(voicemail['id']).put(number=number)
        response.assert_updated()


@fixtures.user()
@fixtures.user()
@fixtures.voicemail()
def test_get_multiple_users_associated_to_voicemail(user1, user2, voicemail):
    with a.user_voicemail(user1, voicemail), a.user_voicemail(user2, voicemail):
        response = confd.voicemails(voicemail['id']).users.get()
        assert_that(
            response.items,
            has_items(
                has_entries(user_id=user1['id'], voicemail_id=voicemail['id']),
                has_entries(user_id=user2['id'], voicemail_id=voicemail['id']),
            )
        )


@fixtures.user()
@fixtures.voicemail()
def test_bus_events(user, voicemail):
    url = confd.users(user['id']).voicemails(voicemail['id']).put
    yield s.check_bus_event, 'config.users.{}.voicemails.updated'.format(user['uuid']), url
    url = confd.users(user['id']).voicemails.delete
    yield s.check_bus_event, 'config.users.{}.voicemails.deleted'.format(user['uuid']), url
