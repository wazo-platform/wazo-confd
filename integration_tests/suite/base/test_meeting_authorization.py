# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
    has_entry,
    has_item,
    is_not,
    none,
    not_none,
)

from . import (
    confd,
    create_confd,
    db,
)
from ..helpers import (
    bus,
    fixtures,
    scenarios as s,
)


@fixtures.ingress_http()
@fixtures.user()
def test_create_meeting_authorization(_, owner):
    owner_uuid = owner['uuid']
    owner_confd = create_confd(user_uuid=owner_uuid)
    with fixtures.user_me_meeting(owner_confd) as meeting:
        unknown_meeting_uuid = '97891324-fed9-46d7-ae00-b40b75178011'
        invalid_guest_uuid = 'invalid'
        guest_uuid = '169e4045-4f2d-4cd1-9933-97c9a1ebb3ff'
        invalid_body = {}
        body = {
            'guest_name': 'jane doe',
        }

        # API can be used without authentication
        response = (
            create_confd()
            .guests(guest_uuid)
            .meetings(meeting['uuid'])
            .authorizations.post(invalid_body)
        )
        response.assert_status(400)

        # Test invalid guest UUID
        response = (
            confd.guests(invalid_guest_uuid)
            .meetings(meeting['uuid'])
            .authorizations.post(body)
        )
        response.assert_status(400)

        # Test invalid meeting UUID
        response = (
            confd.guests(guest_uuid)
            .meetings(unknown_meeting_uuid)
            .authorizations.post(body)
        )
        response.assert_status(404)

        # Test invalid body
        response = (
            confd.guests(guest_uuid)
            .meetings(meeting['uuid'])
            .authorizations.post(invalid_body)
        )
        response.assert_status(400)

        # Setup bus events
        bus_events = bus.BusClient.accumulator(
            'config.meeting_guest_authorizations.created'
        )
        bus_events_user = bus.BusClient.accumulator(
            f'config.users.{owner_uuid}.meeting_guest_authorizations.created'
        )

        # Test creation
        response = (
            confd.guests(guest_uuid).meetings(meeting['uuid']).authorizations.post(body)
        )
        response.assert_status(201)

        # Test bus events
        bus_events.until_assert_that_accumulate(
            has_item(
                has_entries(
                    {
                        'name': 'meeting_guest_authorization_created',
                        'data': has_entries(
                            {
                                'uuid': response.json['uuid'],
                                'guest_name': body['guest_name'],
                            }
                        ),
                    }
                ),
            ),
            timeout=5,
        )
        bus_events_user.until_assert_that_accumulate(
            has_item(
                has_entries(
                    {
                        'name': 'meeting_user_guest_authorization_created',
                        'data': has_entries(
                            {
                                'uuid': response.json['uuid'],
                                'guest_name': body['guest_name'],
                            }
                        ),
                    }
                ),
            ),
            timeout=5,
        )

        # Test max creation
        with db.queries() as queries:
            with queries.insert_max_meeting_authorizations(guest_uuid, meeting['uuid']):
                response = (
                    confd.guests(guest_uuid)
                    .meetings(meeting['uuid'])
                    .authorizations.post(body)
                )

                response.assert_status(400)


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting(name="search", persistent=True, require_authorization=True)
def test_list_search_authorizations_by_user(_, me, another_meeting):
    searches = {'guest_name': 'found'}
    found_guest_uuid = 'a6c156c9-b401-40dc-9939-c1f2492d8572'
    hidden_guest_uuid = 'a6c156c9-b401-40dc-9939-c1f2492d8572'
    my_uuid = me['uuid']
    unknown_uuid = '02b3d964-30ba-4b30-8f9c-e89cbe87b8bc'
    user_confd = create_confd(user_uuid=my_uuid)

    with fixtures.user_me_meeting(
        user_confd
    ) as meeting, fixtures.meeting_authorization(
        found_guest_uuid, meeting, guest_name='found'
    ) as authorization_found, fixtures.meeting_authorization(
        hidden_guest_uuid, meeting, guest_name='hidden'
    ) as authorization_hidden:

        # Test unknown meeting
        response = user_confd.users.me.meetings(unknown_uuid).authorizations.get()
        response.assert_status(404)

        # Test another meeting
        response = user_confd.users.me.meetings(
            another_meeting['uuid']
        ).authorizations.get()
        response.assert_status(404)

        # Test search
        url = user_confd.users.me.meetings(meeting['uuid']).authorizations
        for field, term in searches.items():
            yield check_authorization_search, url, authorization_found, authorization_hidden, field, term


def check_authorization_search(url, meeting, hidden, field, term):
    response = url.get(search=term)

    assert_that(response.items, has_item(has_entry(field, meeting[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: meeting[field]})

    assert_that(response.items, has_item(has_entry('uuid', meeting['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.ingress_http()
@fixtures.user()
def test_sorting_offset_limit_authorizations_by_user(_, me):
    sort1_uuid = 'd8fe7608-687c-4399-ba55-332fb29cb868'
    sort2_uuid = 'a28d1ca7-02a7-4bce-8b84-2b22e900cc01'
    my_uuid = me['uuid']
    user_confd = create_confd(user_uuid=my_uuid)
    with fixtures.user_me_meeting(
        user_confd
    ) as meeting, fixtures.meeting_authorization(
        sort1_uuid, meeting, guest_name='sort1'
    ) as authorization1, fixtures.meeting_authorization(
        sort2_uuid, meeting, guest_name='sort2'
    ) as authorization2:
        url = user_confd.users.me.meetings(meeting['uuid']).authorizations.get

        yield s.check_sorting, url, authorization1, authorization2, 'guest_name', 'sort', 'uuid'

        yield s.check_offset, url, authorization1, authorization2, 'guest_name', 'sort', 'uuid'
        yield s.check_limit, url, authorization1, authorization2, 'guest_name', 'sort', 'uuid'


@fixtures.ingress_http()
@fixtures.meeting()
@fixtures.meeting()
def test_get_meeting_authorization_by_guest(_, meeting, another_meeting):
    unknown_uuid = '97891324-fed9-46d7-ae00-b40b75178011'
    invalid_uuid = 'invalid'
    guest_uuid = '169e4045-4f2d-4cd1-9933-97c9a1ebb3ff'
    another_guest_uuid = '35d77566-357f-46b9-856e-758452148c11'

    def url(guest_uuid, meeting_uuid, authorization_uuid):
        return (
            confd.guests(guest_uuid)
            .meetings(meeting_uuid)
            .authorizations(authorization_uuid)
            .get()
        )

    with fixtures.meeting_authorization(
        guest_uuid, meeting
    ) as authorization, fixtures.meeting_authorization(
        another_guest_uuid, another_meeting
    ) as another_authorization:

        # Test invalid guest_uuid
        url(invalid_uuid, meeting['uuid'], authorization['uuid']).assert_status(400)

        # Test unknown guest_uuid
        url(unknown_uuid, meeting['uuid'], authorization['uuid']).assert_status(404)

        # Test invalid meeting_uuid
        url(guest_uuid, invalid_uuid, authorization['uuid']).assert_status(404)

        # Test unknown meeting_uuid
        url(guest_uuid, unknown_uuid, authorization['uuid']).assert_status(404)

        # Test invalid authorization_uuid
        url(guest_uuid, meeting['uuid'], invalid_uuid).assert_status(404)

        # Test unknown authorization_uuid
        url(guest_uuid, meeting['uuid'], unknown_uuid).assert_status(404)

        # Test stolen guest_uuid
        url(
            guest_uuid, another_meeting['uuid'], another_authorization['uuid']
        ).assert_status(404)

        # Test stolen meeting_uuid
        url(
            another_guest_uuid, meeting['uuid'], another_authorization['uuid']
        ).assert_status(404)

        # Test stolen authorization_uuid
        url(
            another_guest_uuid, another_meeting['uuid'], authorization['uuid']
        ).assert_status(404)

        # Test stolen meeting_uuid & authorization_uuid
        url(another_guest_uuid, meeting['uuid'], authorization['uuid']).assert_status(
            404
        )

        # Test get OK
        url(guest_uuid, meeting['uuid'], authorization['uuid']).assert_status(200)


@fixtures.ingress_http()
@fixtures.meeting()
@fixtures.user()
def test_get_meeting_authorization_by_user(_, another_meeting, me):
    unknown_uuid = '97891324-fed9-46d7-ae00-b40b75178011'
    invalid_uuid = 'invalid'
    guest_uuid = '169e4045-4f2d-4cd1-9933-97c9a1ebb3ff'
    another_guest_uuid = 'd810dacf-ce08-4cea-b7fc-2b08323451bc'
    my_uuid = me['uuid']
    user_confd = create_confd(user_uuid=my_uuid)

    def url(meeting_uuid, authorization_uuid):
        return (
            user_confd.users.me.meetings(meeting_uuid)
            .authorizations(authorization_uuid)
            .get()
        )

    with fixtures.user_me_meeting(
        user_confd
    ) as meeting, fixtures.meeting_authorization(
        guest_uuid, meeting
    ) as authorization, fixtures.meeting_authorization(
        another_guest_uuid, another_meeting
    ) as another_authorization:
        # Test invalid meeting_uuid
        url(invalid_uuid, authorization['uuid']).assert_status(404)

        # Test unknown meeting_uuid
        url(unknown_uuid, authorization['uuid']).assert_status(404)

        # Test another meeting_uuid
        url(another_meeting['uuid'], another_authorization['uuid']).assert_status(404)

        # Test invalid authorization_uuid
        url(meeting['uuid'], invalid_uuid).assert_status(404)

        # Test unknown authorization_uuid
        url(meeting['uuid'], unknown_uuid).assert_status(404)

        # Test get OK
        url(meeting['uuid'], authorization['uuid']).assert_status(200)


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting()
def test_accept_meeting_authorization(_, me, another_meeting):
    guest_uuid = '169e4045-4f2d-4cd1-9933-97c9a1ebb3ff'
    another_guest_uuid = 'd810dacf-ce08-4cea-b7fc-2b08323451bc'
    my_uuid = me['uuid']
    unknown_uuid = '97891324-fed9-46d7-ae00-b40b75178011'
    user_confd = create_confd(user_uuid=my_uuid)

    def url(meeting_uuid, authorization_uuid):
        return (
            user_confd.users.me.meetings(meeting_uuid)
            .authorizations(authorization_uuid)
            .accept.put()
        )

    with fixtures.user_me_meeting(
        user_confd
    ) as meeting, fixtures.meeting_authorization(
        guest_uuid, meeting
    ) as authorization, fixtures.meeting_authorization(
        another_guest_uuid, another_meeting
    ) as another_authorization:

        # Test unknown meeting
        url(unknown_uuid, authorization['uuid']).assert_status(404)

        # Test unknown authorization
        url(meeting['uuid'], unknown_uuid).assert_status(404)

        # Test another meeting
        url(another_meeting['uuid'], another_authorization['uuid']).assert_status(404)

        # Setup bus events
        bus_events = bus.BusClient.accumulator(
            'config.meeting_guest_authorizations.updated'
        )
        bus_events_user = bus.BusClient.accumulator(
            f'config.users.{my_uuid}.meeting_guest_authorizations.updated'
        )

        # Test accept authorization
        response = url(meeting['uuid'], authorization['uuid'])
        response.assert_status(200)
        assert_that(response.json, has_entries(status='accepted'))

        # Test bus events
        bus_events.until_assert_that_accumulate(
            has_item(
                has_entries(
                    {
                        'name': 'meeting_guest_authorization_updated',
                        'data': has_entries(
                            {
                                'uuid': authorization['uuid'],
                                'guest_name': authorization['guest_name'],
                                'status': 'accepted',
                            }
                        ),
                    }
                ),
            ),
            timeout=5,
        )
        bus_events_user.until_assert_that_accumulate(
            has_item(
                has_entries(
                    {
                        'name': 'meeting_user_guest_authorization_updated',
                        'data': has_entries(
                            {
                                'uuid': authorization['uuid'],
                                'guest_name': authorization['guest_name'],
                                'status': 'accepted',
                            }
                        ),
                    }
                ),
            ),
            timeout=5,
        )

        # Guest can see the accepted authorization and sip credentials
        response = (
            confd.guests(guest_uuid)
            .meetings(meeting['uuid'])
            .authorizations(authorization['uuid'])
            .get()
        )
        response.assert_status(200)
        assert_that(
            response.json,
            has_entries(status='accepted', guest_sip_authorization=not_none()),
        )


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting()
def test_reject_meeting_authorization(_, me, another_meeting):
    guest_uuid = '18388400-8f8f-4e76-a487-db3c79cf8d35'
    another_guest_uuid = 'd810dacf-ce08-4cea-b7fc-2b08323451bc'
    my_uuid = me['uuid']
    unknown_uuid = 'ff65a89a-ef00-4c9b-883b-d96ee4186492'
    user_confd = create_confd(user_uuid=my_uuid)

    def url(meeting_uuid, authorization_uuid):
        return (
            user_confd.users.me.meetings(meeting_uuid)
            .authorizations(authorization_uuid)
            .reject.put()
        )

    with fixtures.user_me_meeting(
        user_confd
    ) as meeting, fixtures.meeting_authorization(
        guest_uuid, meeting
    ) as authorization, fixtures.meeting_authorization(
        another_guest_uuid, another_meeting
    ) as another_authorization:

        # Test unknown meeting
        url(unknown_uuid, authorization['uuid']).assert_status(404)

        # Test unknown authorization
        url(meeting['uuid'], unknown_uuid).assert_status(404)

        # Test another meeting
        url(another_meeting['uuid'], another_authorization['uuid']).assert_status(404)

        # Setup bus events
        bus_events = bus.BusClient.accumulator(
            'config.meeting_guest_authorizations.updated'
        )
        bus_events_user = bus.BusClient.accumulator(
            f'config.users.{my_uuid}.meeting_guest_authorizations.updated'
        )

        # Test reject authorization and bus events
        response = url(meeting['uuid'], authorization['uuid'])
        response.assert_status(200)
        assert_that(response.json, has_entries(status='rejected'))

        # Test bus events
        bus_events.until_assert_that_accumulate(
            has_item(
                has_entries(
                    {
                        'name': 'meeting_guest_authorization_updated',
                        'data': has_entries(
                            {
                                'uuid': authorization['uuid'],
                                'guest_name': authorization['guest_name'],
                                'status': 'rejected',
                            }
                        ),
                    }
                ),
            ),
            timeout=5,
        )
        bus_events_user.until_assert_that_accumulate(
            has_item(
                has_entries(
                    {
                        'name': 'meeting_user_guest_authorization_updated',
                        'data': has_entries(
                            {
                                'uuid': authorization['uuid'],
                                'guest_name': authorization['guest_name'],
                                'status': 'rejected',
                            }
                        ),
                    }
                ),
            ),
            timeout=5,
        )

        # Guest can see the authorization is rejected and no sip credentials
        response = (
            confd.guests(guest_uuid)
            .meetings(meeting['uuid'])
            .authorizations(authorization['uuid'])
            .get()
        )
        response.assert_status(200)
        assert_that(
            response.json,
            has_entries(status='rejected', guest_sip_authorization=none()),
        )


@fixtures.ingress_http()
@fixtures.meeting()
@fixtures.user()
def test_delete_meeting_authorization_by_user(_, another_meeting, me):
    unknown_uuid = '97891324-fed9-46d7-ae00-b40b75178011'
    invalid_uuid = 'invalid'
    guest_uuid = '169e4045-4f2d-4cd1-9933-97c9a1ebb3ff'
    another_guest_uuid = 'd810dacf-ce08-4cea-b7fc-2b08323451bc'
    my_uuid = me['uuid']
    user_confd = create_confd(user_uuid=my_uuid)

    def url(meeting_uuid, authorization_uuid):
        return (
            user_confd.users.me.meetings(meeting_uuid)
            .authorizations(authorization_uuid)
            .delete()
        )

    with fixtures.user_me_meeting(
        user_confd
    ) as meeting, fixtures.meeting_authorization(
        guest_uuid, meeting
    ) as authorization, fixtures.meeting_authorization(
        another_guest_uuid, another_meeting
    ) as another_authorization:
        # Test invalid meeting_uuid
        url(invalid_uuid, authorization['uuid']).assert_status(404)

        # Test unknown meeting_uuid
        url(unknown_uuid, authorization['uuid']).assert_status(404)

        # Test another meeting_uuid
        url(another_meeting['uuid'], another_authorization['uuid']).assert_status(404)

        # Test invalid authorization_uuid
        url(meeting['uuid'], invalid_uuid).assert_status(404)

        # Test unknown authorization_uuid
        url(meeting['uuid'], unknown_uuid).assert_status(404)

        # Setup bus events
        bus_events = bus.BusClient.accumulator(
            'config.meeting_guest_authorizations.deleted'
        )
        bus_events_user = bus.BusClient.accumulator(
            f'config.users.{my_uuid}.meeting_guest_authorizations.deleted'
        )

        # Test delete OK
        url(meeting['uuid'], authorization['uuid']).assert_status(204)

        # Test bus events
        bus_events.until_assert_that_accumulate(
            has_item(
                has_entries(
                    {
                        'name': 'meeting_guest_authorization_deleted',
                        'data': has_entries(
                            {
                                'uuid': authorization['uuid'],
                                'guest_name': authorization['guest_name'],
                            }
                        ),
                    }
                ),
            ),
            timeout=5,
        )
        bus_events_user.until_assert_that_accumulate(
            has_item(
                has_entries(
                    {
                        'name': 'meeting_user_guest_authorization_deleted',
                        'data': has_entries(
                            {
                                'uuid': authorization['uuid'],
                                'guest_name': authorization['guest_name'],
                            }
                        ),
                    }
                ),
            ),
            timeout=5,
        )

        # Test delete again
        url(meeting['uuid'], authorization['uuid']).assert_status(404)

        # Meeting is still present
        response = user_confd.users.me.meetings(meeting['uuid']).get()

        response.assert_status(200)


def test_unimplemented_methods():
    guest_uuid = '5797d37d-bee4-4b59-861e-a372bbb64c60'
    meeting_uuid = '83ea3511-d655-4e0f-b7a9-57850f767a59'
    authorization_uuid = '7da4d46b-fe5a-4ebd-b7ac-ca7d9152cc0f'
    user_uuid = '48c7d8a1-dbce-4681-b307-061b9f80b204'
    user_confd = create_confd(user_uuid=user_uuid)

    # Guests list authorizations
    response = (
        create_confd().guests(guest_uuid).meetings(meeting_uuid).authorizations.get()
    )
    response.assert_status(405)

    # Guests update authorization
    response = (
        create_confd()
        .guests(guest_uuid)
        .meetings(meeting_uuid)
        .authorizations(authorization_uuid)
        .update({})
    )
    response.assert_status(405)

    # Guests update authorization
    response = (
        create_confd()
        .guests(guest_uuid)
        .meetings(meeting_uuid)
        .authorizations(authorization_uuid)
        .delete()
    )
    response.assert_status(405)

    # Users create authorizations
    response = user_confd.users.me.meetings(meeting_uuid).authorizations.create({})
    response.assert_status(405)

    # Users update authorization
    response = (
        user_confd.users.me.meetings(meeting_uuid)
        .authorizations(authorization_uuid)
        .update({})
    )
    response.assert_status(405)

    # Users get authorization accept
    response = (
        user_confd.users.me.meetings(meeting_uuid)
        .authorizations(authorization_uuid)
        .accept.get()
    )
    response.assert_status(405)

    # Users delete authorization accept
    response = (
        user_confd.users.me.meetings(meeting_uuid)
        .authorizations(authorization_uuid)
        .accept.delete()
    )
    response.assert_status(405)

    # Users get authorization reject
    response = (
        user_confd.users.me.meetings(meeting_uuid)
        .authorizations(authorization_uuid)
        .reject.get()
    )
    response.assert_status(405)

    # Users delete authorization reject
    response = (
        user_confd.users.me.meetings(meeting_uuid)
        .authorizations(authorization_uuid)
        .reject.delete()
    )
    response.assert_status(405)
