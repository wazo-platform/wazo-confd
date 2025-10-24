# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, empty, has_entries, is_not, none

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


@fixtures.call_filter()
@fixtures.user()
def test_associate_errors(call_filter, user):
    response = confd.callfilters(FAKE_ID).surrogates.users.put(users=[user])
    response.assert_status(404)

    url = confd.callfilters(call_filter['id']).surrogates.users
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'users', 123)
    s.check_bogus_field_returns_error(url, 'users', None)
    s.check_bogus_field_returns_error(url, 'users', True)
    s.check_bogus_field_returns_error(url, 'users', 'string')
    s.check_bogus_field_returns_error(url, 'users', [123])
    s.check_bogus_field_returns_error(url, 'users', [None])
    s.check_bogus_field_returns_error(url, 'users', ['string'])
    s.check_bogus_field_returns_error(url, 'users', [{}])
    s.check_bogus_field_returns_error(url, 'users', [{'uuid': None}])
    s.check_bogus_field_returns_error(url, 'users', [{'uuid': 1}, {'uuid': None}])
    s.check_bogus_field_returns_error(url, 'users', [{'not_uuid': 123}])
    s.check_bogus_field_returns_error(url, 'users', [{'uuid': FAKE_UUID}])


@fixtures.call_filter()
@fixtures.user()
def test_associate(call_filter, user):
    response = confd.callfilters(call_filter['id']).surrogates.users.put(users=[user])
    response.assert_updated()


@fixtures.call_filter()
@fixtures.user()
@fixtures.user()
@fixtures.user()
def test_associate_multiple(call_filter, user1, user2, user3):
    response = confd.callfilters(call_filter['id']).surrogates.users.put(
        users=[user3, user1, user2]
    )
    response.assert_updated()

    response = confd.callfilters(call_filter['id']).get()
    assert_that(
        response.item,
        has_entries(
            surrogates=has_entries(
                users=contains(
                    has_entries(uuid=user3['uuid']),
                    has_entries(uuid=user1['uuid']),
                    has_entries(uuid=user2['uuid']),
                )
            )
        ),
    )


@fixtures.call_filter()
@fixtures.user()
def test_associate_same_user(call_filter, user):
    response = confd.callfilters(call_filter['id']).surrogates.users.put(
        users=[user, user]
    )
    response.assert_status(400)


@fixtures.call_filter()
@fixtures.user()
def test_associate_recipient_to_surrogate(call_filter, user):
    with a.call_filter_recipient_user(call_filter, user):
        response = confd.callfilters(call_filter['id']).surrogates.users.put(
            users=[user]
        )
        response.assert_status(400)


@fixtures.call_filter(wazo_tenant=MAIN_TENANT)
@fixtures.call_filter(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_call_filter, sub_call_filter, main_user, sub_user):
    response = confd.callfilters(main_call_filter['id']).surrogates.users.put(
        users=[{'uuid': main_user['uuid']}], wazo_tenant=SUB_TENANT
    )
    response.assert_match(404, e.not_found('CallFilter'))

    response = confd.callfilters(sub_call_filter['id']).surrogates.users.put(
        users=[{'uuid': main_user['uuid']}], wazo_tenant=SUB_TENANT
    )
    response.assert_match(400, e.not_found('User'))

    response = confd.callfilters(main_call_filter['id']).surrogates.users.put(
        users=[{'uuid': sub_user['uuid']}], wazo_tenant=MAIN_TENANT
    )
    response.assert_match(400, e.different_tenant())


@fixtures.call_filter()
@fixtures.user()
@fixtures.user()
def test_get_users_associated_to_call_filter(call_filter, user1, user2):
    with a.call_filter_surrogate_user(call_filter, user2, user1):
        response = confd.callfilters(call_filter['id']).get()
        assert_that(
            response.item,
            has_entries(
                surrogates=has_entries(
                    users=contains(
                        has_entries(
                            uuid=user2['uuid'],
                            firstname=user2['firstname'],
                            lastname=user2['lastname'],
                            member_id=is_not(none()),
                        ),
                        has_entries(
                            uuid=user1['uuid'],
                            firstname=user1['firstname'],
                            lastname=user1['lastname'],
                            member_id=is_not(none()),
                        ),
                    )
                )
            ),
        )


@fixtures.call_filter()
@fixtures.user()
@fixtures.user()
def test_dissociate(call_filter, user1, user2):
    with a.call_filter_surrogate_user(call_filter, user1, user2):
        response = confd.callfilters(call_filter['id']).surrogates.users.put(users=[])
        response.assert_updated()


@fixtures.call_filter()
@fixtures.user()
@fixtures.user()
def test_delete_call_filter_when_call_filter_and_user_associated(
    call_filter, user1, user2
):
    with a.call_filter_surrogate_user(call_filter, user1, user2, check=False):
        confd.callfilters(call_filter['id']).delete().assert_deleted()

        deleted_call_filter = confd.callfilters(call_filter['id']).get
        s.check_resource_not_found(deleted_call_filter, 'CallFilter')

        # When the relation will be added,
        # we should check if users have the key.callfilters to empty


@fixtures.call_filter()
@fixtures.call_filter()
@fixtures.user()
def test_delete_user_when_call_filter_and_user_associated(
    call_filter1, call_filter2, user
):
    with a.call_filter_surrogate_user(
        call_filter1, user, check=False
    ), a.call_filter_surrogate_user(call_filter2, user, check=False):
        confd.users(user['uuid']).delete().assert_deleted()

        response = confd.callfilters(call_filter1['id']).get()
        assert_that(response.item['surrogates']['users'], empty())

        response = confd.callfilters(call_filter2['id']).get()
        assert_that(response.item['surrogates']['users'], empty())


@fixtures.call_filter()
@fixtures.user()
def test_bus_events(call_filter, user):
    url = confd.callfilters(call_filter['id']).surrogates.users.put
    body = {'users': [user]}
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event('call_filter_surrogate_users_associated', headers, url, body)


@fixtures.call_filter()
@fixtures.user()
def test_get_surrogates_callfilter_exten(call_filter, user):
    with a.call_filter_surrogate_user(call_filter, user):
        response = confd.callfilters(call_filter['id']).get()
        member_id = response.item['surrogates']['users'][0]['member_id']

        assert_that(
            response.item,
            has_entries(
                surrogates=has_entries(
                    users=contains(
                        has_entries(exten='*37{}'.format(member_id), uuid=user['uuid']),
                    )
                )
            ),
        )


@fixtures.call_filter()
@fixtures.user()
def test_get_surrogates_callfilter_exten_when_disabled(call_filter, user):
    response = confd.extensions.features.get(search="bsfilter")
    feature = response.items[0]
    confd.extensions.features(feature['uuid']).put({'enabled': False}).assert_updated()

    with a.call_filter_surrogate_user(call_filter, user):
        response = confd.callfilters(call_filter['id']).get()

        assert_that(
            response.item,
            has_entries(
                surrogates=has_entries(
                    users=contains(has_entries(exten=None, uuid=user['uuid']))
                )
            ),
        )

    confd.extensions.features(feature['uuid']).put(
        {'enabled': feature['enabled']}
    ).assert_updated()
