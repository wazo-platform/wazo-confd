# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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


def test_associate_errors():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        fake_user = confd.users(FAKE_ID).voicemails(voicemail['id']).put
        fake_voicemail = confd.users(user['id']).voicemails(FAKE_ID).put

        s.check_resource_not_found(fake_user, 'User')
        s.check_resource_not_found(fake_voicemail, 'Voicemail')



def test_dissociate_errors():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        fake_user = confd.users(FAKE_ID).voicemails.delete

        s.check_resource_not_found(fake_user, 'User')



def test_get_errors():
    with fixtures.user() as user:
        fake_user = confd.users(FAKE_ID).voicemails.get
        fake_voicemail = confd.voicemails(FAKE_ID).users.get

        s.check_resource_not_found(fake_user, 'User')
        s.check_resource_not_found(fake_voicemail, 'Voicemail')



def test_associate():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        response = confd.users(user['id']).voicemails(voicemail['id']).put()
        response.assert_updated()



def test_associate_using_uuid():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        response = confd.users(user['id']).voicemails(voicemail['id']).put()
        response.assert_updated()



def test_associate_when_already_associated():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user, voicemail):
            response = confd.users(user['id']).voicemails(voicemail['id']).put()
            response.assert_updated()


def test_associate_multiple_users_to_voicemail():
    with fixtures.user() as user1, fixtures.user() as user2, fixtures.voicemail() as voicemail:
        response = confd.users(user1['id']).voicemails(voicemail['id']).put()
        response.assert_updated()

        response = confd.users(user2['id']).voicemails(voicemail['id']).put()
        response.assert_updated()



def test_get_user_voicemail_association():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        expected = has_entries({'user_id': user['id'],
                                'voicemail_id': voicemail['id']})

        with a.user_voicemail(user, voicemail):
            response = confd.users(user['id']).voicemails.get()
            assert_that(response.item, expected)

            response = confd.users(user['uuid']).voicemails.get()
            assert_that(response.item, expected)



def test_get_user_voicemail_association_multi_tenant():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user, voicemail):
            response = confd.users(user['id']).voicemails.get(wazo_tenant=SUB_TENANT)
            response.assert_match(404, e.not_found('User'))


def test_get_user_voicemail_after_dissociation():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        h.user_voicemail.associate(user['id'], voicemail['id'])
        h.user_voicemail.dissociate(user['id'], voicemail['id'])

        response = confd.users(user['id']).voicemails.get()
        response.assert_match(404, e.not_found('UserVoicemail'))

        response = confd.users(user['uuid']).voicemails.get()
        response.assert_match(404, e.not_found('UserVoicemail'))



def test_associate_multi_tenant():
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as __, fixtures.voicemail(context='main_ctx') as main_vm, fixtures.voicemail(context='sub_ctx') as sub_vm, fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user:
        response = confd.users(main_user['uuid']).voicemails(sub_vm['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('User'))

        response = confd.users(sub_user['uuid']).voicemails(main_vm['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Voicemail'))

        response = confd.users(main_user['uuid']).voicemails(sub_vm['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user, voicemail, check=False):
            response = confd.users(user['id']).voicemails.delete()
            response.assert_deleted()


def test_dissociate_using_uuid():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user, voicemail, check=False):
            response = confd.users(user['uuid']).voicemails.delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        response = confd.users(user['id']).voicemails.delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.user(wazo_tenant=MAIN_TENANT) as user:
        response = confd.users(user['uuid']).voicemails.delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('User'))



def test_get_voicemail_relation():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user, voicemail):
            response = confd.users(user['id']).get()
            assert_that(
                response.item,
                has_entries(
                    voicemail=has_entries(id=voicemail['id'], name=voicemail['name']),
                )
            )


def test_get_users_relation():
    with fixtures.user() as u1, fixtures.user() as u2, fixtures.voicemail() as voicemail:
        with a.user_voicemail(u1, voicemail), a.user_voicemail(u2, voicemail):
            response = confd.voicemails(voicemail['id']).get()
            assert_that(
                response.item['users'],
                contains_inanyorder(
                    has_entries(uuid=u1['uuid'], firstname=u1['firstname'], lastname=u1['lastname']),
                    has_entries(uuid=u2['uuid'], firstname=u2['firstname'], lastname=u2['lastname']),
                )
            )


def test_delete_user_when_still_associated():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user, voicemail):
            response = confd.users(user['id']).delete()
            response.assert_match(400, e.resource_associated('User', 'Voicemail'))


def test_delete_voicemail_when_still_associated():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user, voicemail):
            response = confd.voicemails(voicemail['id']).delete()
            response.assert_match(400, e.resource_associated('Voicemail', 'User'))


def test_edit_voicemail_when_still_associated():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        number = h.voicemail.find_available_number(voicemail['context'])
        with a.user_voicemail(user, voicemail):
            response = confd.voicemails(voicemail['id']).put(number=number)
            response.assert_updated()



def test_get_multiple_users_associated_to_voicemail():
    with fixtures.user() as user1, fixtures.user() as user2, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user1, voicemail), a.user_voicemail(user2, voicemail):
            response = confd.voicemails(voicemail['id']).users.get()
            assert_that(
                response.items,
                has_items(
                    has_entries(user_id=user1['id'], voicemail_id=voicemail['id']),
                    has_entries(user_id=user2['id'], voicemail_id=voicemail['id']),
                )
            )


def test_get_users_relation_multi_tenant():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user, voicemail):
            response = confd.voicemails(voicemail['id']).users.get(wazo_tenant=SUB_TENANT)
            response.assert_match(404, e.not_found('Voicemail'))


def test_get_user_voicemail_legacy_multi_tenant():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        with a.user_voicemail(user, voicemail):
            response = confd.users(user['id']).voicemail.get(wazo_tenant=SUB_TENANT)
            response.assert_match(404, e.not_found('User'))


def test_associate_legacy_multi_tenant():
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as __, fixtures.voicemail(context='main_ctx') as main_vm, fixtures.voicemail(context='sub_ctx') as sub_vm, fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user:
        response = confd.users(main_user['uuid']).voicemail.post(
            voicemail_id=sub_vm['id'],
            wazo_tenant=SUB_TENANT,
        )
        response.assert_match(404, e.not_found('User'))

        response = confd.users(sub_user['uuid']).voicemail.post(
            voicemail_id=main_vm['id'],
            wazo_tenant=SUB_TENANT,
        )
        response.assert_match(400, e.not_found('Voicemail'))

        response = confd.users(main_user['uuid']).voicemail.post(
            voicemail_id=sub_vm['id'],
            wazo_tenant=MAIN_TENANT,
        )
        response.assert_match(400, e.different_tenant())



def test_dissociate_legacy_multi_tenant():
    with fixtures.user(wazo_tenant=MAIN_TENANT) as user:
        response = confd.users(user['uuid']).voicemail.delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('User'))



def test_bus_events():
    with fixtures.user() as user, fixtures.voicemail() as voicemail:
        url = confd.users(user['id']).voicemails(voicemail['id']).put
        s.check_bus_event('config.users.{}.voicemails.updated'.format(user['uuid']), url)
        url = confd.users(user['id']).voicemails.delete
        s.check_bus_event('config.users.{}.voicemails.deleted'.format(user['uuid']), url)

