# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, has_entries, has_items

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import helpers as h
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

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


@fixtures.context(label='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(label='sub_ctx', wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_ctx, sub_ctx, main_user, sub_user):
    with fixtures.voicemail(context=main_ctx['name']) as main_vm:
        with fixtures.voicemail(context=sub_ctx['name']) as sub_vm:
            response = (
                confd.users(main_user['uuid'])
                .voicemails(sub_vm['id'])
                .put(wazo_tenant=SUB_TENANT)
            )
            response.assert_match(404, e.not_found('User'))

            response = (
                confd.users(sub_user['uuid'])
                .voicemails(main_vm['id'])
                .put(wazo_tenant=SUB_TENANT)
            )
            response.assert_match(404, e.not_found('Voicemail'))

            response = (
                confd.users(main_user['uuid'])
                .voicemails(sub_vm['id'])
                .put(wazo_tenant=MAIN_TENANT)
            )
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
                voicemail=has_entries(id=voicemail['id'], name=voicemail['name'])
            ),
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
                has_entries(
                    uuid=u1['uuid'], firstname=u1['firstname'], lastname=u1['lastname']
                ),
                has_entries(
                    uuid=u2['uuid'], firstname=u2['firstname'], lastname=u2['lastname']
                ),
            ),
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
@fixtures.voicemail()
def test_bus_events(user, voicemail):
    headers = {
        'tenant_uuid': voicemail['tenant_uuid'],
        f'user_uuid:{user["uuid"]}': True,
    }

    url = confd.users(user['id']).voicemails(voicemail['id']).put
    yield s.check_event, 'user_voicemail_associated', headers, url

    url = confd.users(user['id']).voicemails.delete
    yield s.check_event, 'user_voicemail_dissociated', headers, url


@fixtures.user()
@fixtures.voicemail()
def test_list_user_voicemail(user, voicemail):
    with a.user_voicemail(user, voicemail):
        response = confd.users(user['uuid']).voicemails.get()
        del voicemail['users']
        assert_that(response.items, contains_inanyorder(has_entries(voicemail)))


@fixtures.context(label='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(label='sub_ctx', wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_list_user_voicemail_multi_tenant(main_ctx, sub_ctx, main_user, sub_user):
    with fixtures.voicemail(context=main_ctx['name']) as main_vm:
        with fixtures.voicemail(context=sub_ctx['name']) as sub_vm:
            with a.user_voicemail(main_user, main_vm), a.user_voicemail(
                sub_user, sub_vm
            ):
                response = confd.users(main_user['uuid']).voicemails.get(
                    wazo_tenant=SUB_TENANT
                )
                response.assert_match(404, e.not_found(resource='User'))

                response = confd.users(sub_user['uuid']).voicemails.get(
                    wazo_tenant=MAIN_TENANT
                )
                assert_that(response.items[0], has_entries(name=sub_vm['name']))


@fixtures.user()
@fixtures.voicemail_zonemessages(name='eu-fr')
def test_create_and_associate(user, _):
    number, context = h.voicemail.generate_number_and_context()

    parameters = {
        'name': 'full',
        'number': number,
        'context': context,
        'email': 'test@example.com',
        'pager': 'test@example.com',
        'language': 'en_US',
        'timezone': 'eu-fr',
        'password': '1234',
        'max_messages': 10,
        'attach_audio': True,
        'ask_password': False,
        'delete_messages': True,
        'enabled': True,
        'options': [["saycid", "yes"], ["emailbody", "this\nis\ra\temail|body"]],
    }

    response = confd.users(user['uuid']).voicemails.post(parameters)
    response.assert_created('voicemails')
    assert_that(
        response.item,
        has_entries(
            name='full',
            number=number,
            context=context,
            email='test@example.com',
            pager='test@example.com',
            language='en_US',
            timezone='eu-fr',
            password='1234',
            max_messages=10,
            attach_audio=True,
            ask_password=False,
            delete_messages=True,
            enabled=True,
            options=has_items(
                ["saycid", "yes"], ["emailbody", "this\nis\ra\temail|body"]
            ),
        ),
    )
