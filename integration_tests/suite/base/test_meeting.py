# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from base64 import b64encode
from datetime import datetime, timedelta, timezone

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    has_entries,
    has_entry,
    has_item,
    has_items,
    has_properties,
    is_not,
    none,
    not_,
    not_none,
)

from ..helpers import bus
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import BaseIntegrationTest, confd, create_confd, db

FAKE_UUID = '99999999-9999-4999-9999-999999999999'


@fixtures.user()
def test_get_errors(me):
    fake_get = confd.meetings(FAKE_UUID).get
    s.check_resource_not_found(fake_get, 'Meeting')

    user_confd = create_confd(user_uuid=me['uuid'])
    fake_get = user_confd.users.me.meetings(FAKE_UUID).get
    s.check_resource_not_found(fake_get, 'Meeting')


@fixtures.user()
def test_post_errors(me):
    url = confd.meetings
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')

    user_confd = create_confd(user_uuid=me['uuid'])
    url = user_confd.users.me.meetings
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')


@fixtures.ingress_http()
@fixtures.meeting()
def test_put_errors(_, meeting):
    url = confd.meetings(meeting['uuid'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


@fixtures.ingress_http()
@fixtures.user()
def test_put_errors_users_me(_, me):
    user_confd = create_confd(user_uuid=me['uuid'])
    with fixtures.user_me_meeting(user_confd) as meeting:
        url = user_confd.users.me.meetings(meeting['uuid'])
        error_checks(url.put)
        s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', 123)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', 'a' * 513)
    s.check_bogus_field_returns_error(url, 'persistent', None)
    s.check_bogus_field_returns_error(url, 'persistent', 42)
    s.check_bogus_field_returns_error(url, 'persistent', 'invalid')
    s.check_bogus_field_returns_error(url, 'persistent', [])
    s.check_bogus_field_returns_error(url, 'persistent', {})


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT, uri='http://main')
@fixtures.ingress_http(wazo_tenant=SUB_TENANT, uri='http://sub')
@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main_ingress, sub_ingress, main, sub):
    response = confd.meetings.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(
            has_item(
                has_entries(
                    uuid=main['uuid'],
                    ingress_http_uri=main_ingress['uri'],
                )
            ),
            not_(has_item(has_entries(uuid=sub['uuid']))),
        ),
    )

    response = confd.meetings.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(
            not_(has_item(has_entries(uuid=main['uuid']))),
            has_item(
                has_entries(
                    uuid=sub['uuid'],
                    ingress_http_uri=sub_ingress['uri'],
                ),
            ),
        ),
    )

    response = confd.meetings.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(
            has_entries(
                uuid=main['uuid'],
                ingress_http_uri=main_ingress['uri'],
            ),
            has_entries(
                uuid=sub['uuid'],
                ingress_http_uri=sub_ingress['uri'],
            ),
        ),
    )


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting(name='ignored')
def test_list_user_me(_, me, __):
    user_confd = create_confd(user_uuid=me['uuid'])
    with fixtures.user_me_meeting(user_confd) as mine_1, fixtures.user_me_meeting(
        user_confd
    ) as mine_2:
        response = user_confd.users.me.meetings.get()
        assert_that(
            response,
            has_properties(
                total=equal_to(2),
                items=contains_inanyorder(mine_1, mine_2),
            ),
        )


@fixtures.ingress_http()
@fixtures.meeting(name="search", persistent=True, require_authorization=True)
@fixtures.meeting(name="hidden", persistent=False, require_authorization=False)
def test_search(_, meeting, hidden):
    url = confd.meetings
    searches = {'name': 'search'}

    for field, term in searches.items():
        check_search(url, meeting, hidden, field, term)

    response = url.get(persistent=True)
    assert_that(response.items, has_item(meeting))
    assert_that(response.items, is_not(has_item(hidden)))

    response = url.get(persistent=False)
    assert_that(response.items, has_item(hidden))
    assert_that(response.items, is_not(has_item(meeting)))

    response = url.get(require_authorization=False)
    assert_that(response.items, has_item(hidden))
    assert_that(response.items, is_not(has_item(meeting)))


def check_search(url, meeting, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, meeting[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: meeting[field]})

    assert_that(response.items, has_item(has_entry('uuid', meeting['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.ingress_http()
@fixtures.meeting(name="sort1")
@fixtures.meeting(name="sort2")
def test_sorting_offset_limit(_, meeting1, meeting2):
    url = confd.meetings.get
    s.check_sorting(url, meeting1, meeting2, 'name', 'sort', 'uuid')

    s.check_offset(url, meeting1, meeting2, 'name', 'sort', 'uuid')
    s.check_limit(url, meeting1, meeting2, 'name', 'sort', 'uuid')


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting()
def test_get(_, me, other_meeting):
    user_confd = create_confd(user_uuid=me['uuid'])
    with fixtures.user_me_meeting(user_confd) as mine:
        response = confd.meetings(other_meeting['uuid']).get()
        assert_that(response.item, has_entries(uuid=other_meeting['uuid']))

        response = confd.guests.me.meetings(other_meeting['uuid']).get()
        assert_that(response.item, has_entries(uuid=other_meeting['uuid']))

        response = user_confd.users.me.meetings(other_meeting['uuid']).get()
        assert_that(response.item, has_entries(uuid=other_meeting['uuid']))

        response = user_confd.users.me.meetings(mine['uuid']).get()
        assert_that(response.item, has_entries(name=mine['name']))


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(_, __, main, sub):
    response = confd.meetings(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Meeting'))

    response = confd.meetings(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_no_ingress_http_configured():
    response = confd.meetings.post(name='error')
    assert_that(
        response,
        has_properties(
            status=503,
            json=contains('no Ingress HTTP configured'),
        ),
    )


@fixtures.ingress_http()
def test_create_no_meetingjoin_extension_feature(_, request):
    extension = confd.extensions.features.get(feature='meetingjoin').items[0]
    extension['enabled'] = False
    response = confd.extensions.features(extension['uuid']).put(**extension)

    def enable_meetingjoin():
        extension['enabled'] = True
        confd.extensions.features(extension['uuid']).put(**extension)

    request.addfinalizer(enable_meetingjoin)

    response = confd.meetings.post(name='no exten')
    try:
        assert_that(response.item, has_entries(exten=None))
    finally:
        confd.meetings.delete(response.item['uuid'])


@fixtures.ingress_http()
@fixtures.user()
def test_create_minimal_parameters(ingress_http, me):
    response = confd.meetings.post(name='minimal')
    response.assert_created('meetings')

    assert_that(
        response.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            uuid=not_(empty()),
            name='minimal',
            ingress_http_uri=ingress_http['uri'],
            persistent=False,
            exten=not_none(),
            require_authorization=False,
        ),
    )

    confd.meetings(response.item['uuid']).delete().assert_deleted()

    user_confd = create_confd(user_uuid=me['uuid'])
    response = user_confd.users.me.meetings.post(name='minimal')
    response.assert_created('meetings')

    assert_that(
        response.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            uuid=not_(empty()),
            owner_uuids=contains_inanyorder(me['uuid']),
            name='minimal',
            ingress_http_uri=ingress_http['uri'],
            persistent=False,
            exten=not_none(),
            require_authorization=False,
        ),
    )

    confd.meetings(response.item['uuid']).delete().assert_deleted()


@fixtures.ingress_http(uri='https://wazo.example.com:10443')
@fixtures.user()
@fixtures.user()
def test_create_all_parameters(ingress_http, me, owner):
    parameters = {
        'name': 'allparameter',
        'owner_uuids': [owner['uuid']],
        'persistent': True,
        'require_authorization': True,
    }

    response = confd.meetings.post(**parameters)
    response.assert_created('meetings')
    assert_that(
        response.item,
        has_entries(
            name=parameters['name'],
            tenant_uuid=MAIN_TENANT,
            owner_uuids=contains_inanyorder(owner['uuid']),
            ingress_http_uri=ingress_http['uri'],
            persistent=True,
            creation_time=not_none(),
            exten=not_none(),
            require_authorization=True,
        ),
    )
    confd.meetings(response.item['uuid']).delete().assert_deleted()

    user_confd = create_confd(user_uuid=me['uuid'])
    response = user_confd.users.me.meetings.post(**parameters)
    response.assert_created('meetings')
    assert_that(
        response.item,
        has_entries(
            name=parameters['name'],
            tenant_uuid=MAIN_TENANT,
            ingress_http_uri=ingress_http['uri'],
            owner_uuids=contains_inanyorder(me['uuid'], owner['uuid']),
            persistent=True,
            creation_time=not_none(),
            exten=not_none(),
            require_authorization=True,
        ),
    )
    confd.meetings(response.item['uuid']).delete().assert_deleted()


@fixtures.ingress_http()
def test_guest_endpoint_sip_creation(_):
    # Create without guest SIP template should fail
    with db.queries() as queries:
        with queries.tenant_guest_sip_template_temporarily_disabled(MAIN_TENANT):
            response = confd.meetings.post({'name': 'testing'})
            response.assert_status(503)

    response = confd.meetings.post({'name': 'testing'})
    meeting = response.item

    endpoint_sip_name = 'wazo-meeting-{uuid}-guest'.format(**meeting)
    response = confd.endpoints.sip.get(name=endpoint_sip_name)
    assert_that(response.total, equal_to(1))

    endpoint_sip = response.items[0]
    endpoint_username = None
    endpoint_password = None
    endpoint_context = None

    for option, value in endpoint_sip['auth_section_options']:
        if option == 'username':
            endpoint_username = value
        elif option == 'password':
            endpoint_password = value

    for option, value in endpoint_sip['endpoint_section_options']:
        if option == 'context':
            endpoint_context = value

    assert_that(endpoint_username, not_none())
    assert_that(endpoint_password, not_none())
    assert_that(endpoint_context, equal_to('wazo-meeting-guest'))

    guest_sip_authorization = b64encode(
        '{}:{}'.format(endpoint_username, endpoint_password).encode()
    ).decode()
    assert_that(
        meeting,
        has_entries(
            guest_sip_authorization=guest_sip_authorization,
        ),
    )

    response = confd.meetings(meeting['uuid']).delete()
    response.assert_deleted()

    response = confd.endpoints.sip(endpoint_sip['uuid']).get()
    response.assert_status(404)


@fixtures.ingress_http()
def test_create_without_name(_):
    response = confd.meetings.post()
    response.assert_status(400)


@fixtures.ingress_http()
@fixtures.user()
def test_create_require_authorization(ingress_http, me):
    response = confd.meetings.post(
        name='require_authorization_false', require_authorization=False
    )

    assert_that(
        response.item,
        has_entries(
            guest_sip_authorization=not_(none()),
        ),
    )
    confd.meetings(response.item['uuid']).delete().assert_deleted()

    response = confd.meetings.post(
        name='require_authorization_true', require_authorization=True
    )

    assert_that(
        response.item,
        has_entries(
            guest_sip_authorization=none(),
        ),
    )
    confd.meetings(response.item['uuid']).delete().assert_deleted()


@fixtures.ingress_http()
@fixtures.meeting()
def test_edit_minimal_parameters(_, meeting):
    response = confd.meetings(meeting['uuid']).put()
    response.assert_updated()


@fixtures.ingress_http()
@fixtures.meeting()
@fixtures.user()
def test_edit_all_parameters(_, meeting, some_user):
    parameters = {
        'name': 'editallparameter',
        'owner_uuids': [some_user['uuid']],
        'require_authorization': True,
    }
    response = confd.meetings(meeting['uuid']).put(
        creation_time='2021-12-06T18:55:58.961760+00:00', **parameters
    )
    response.assert_updated()

    response = confd.meetings(meeting['uuid']).get()
    assert_that(
        response.item, has_entries(creation_time=meeting['creation_time'], **parameters)
    )


@fixtures.ingress_http()
@fixtures.user()
@fixtures.user()
@fixtures.meeting()
def test_edit_all_parameters_users_me(_, me, other_user, other_meeting):
    user_confd = create_confd(user_uuid=me['uuid'])
    with fixtures.user_me_meeting(user_confd) as mine:
        parameters = {
            'name': 'editallparameter',
            'owner_uuids': [other_user['uuid']],
            'require_authorization': True,
        }
        expected_parameters = {
            'name': 'editallparameter',
            'owner_uuids': [me['uuid'], other_user['uuid']],
            'creation_time': mine['creation_time'],
        }

        response = user_confd.users.me.meetings(mine['uuid']).put(
            creation_time='2021-12-06T18:55:58.961760+00:00', **parameters
        )
        response.assert_updated()

        response = user_confd.users.me.meetings(mine['uuid']).get()
        assert_that(response.item, has_entries(expected_parameters))

        response = user_confd.users.me.meetings(other_meeting['uuid']).put(**parameters)
        response.assert_match(404, e.not_found(resource='Meeting'))


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(_, __, main, sub):
    response = confd.meetings(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Meeting'))

    response = confd.meetings(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.ingress_http()
@fixtures.meeting()
def test_delete(_, meeting):
    response = confd.meetings(meeting['uuid']).delete()
    response.assert_deleted()
    confd.meetings(meeting['uuid']).get().assert_status(404)


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting()
def test_delete_users_me(_, me, other_meeting):
    user_confd = create_confd(user_uuid=me['uuid'])
    with fixtures.user_me_meeting(user_confd) as mine:
        response = user_confd.users.me.meetings(mine['uuid']).delete()
        response.assert_deleted()
        confd.meetings(mine['uuid']).get().assert_status(404)

        response = user_confd.users.me.meetings(other_meeting['uuid']).delete()
        response.assert_match(404, e.not_found(resource='Meeting'))


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(_, __, main, sub):
    response = confd.meetings(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Meeting'))

    response = confd.meetings(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.ingress_http()
@fixtures.meeting()
def test_bus_events(_, meeting):
    url = confd.meetings(meeting['uuid'])
    headers = {'tenant_uuid': meeting['tenant_uuid']}

    s.check_event('meeting_created', headers, confd.meetings.post, {'name': 'meeting'})

    headers['meeting_uuid'] = meeting['uuid']
    s.check_event('meeting_updated', headers, url.put)
    s.check_event('meeting_deleted', headers, url.delete)


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting()
def test_bus_events_progress(_, me, meeting):
    headers = {'tenant_uuid': meeting['tenant_uuid']}
    s.check_event(
        'meeting_progress',
        headers,
        bus.BusClient.send_meeting_reload_complete_event,
        meeting,
    )

    my_uuid = me['uuid']
    user_confd = create_confd(user_uuid=my_uuid)
    with fixtures.user_me_meeting(user_confd) as mine:
        headers = {'tenant_uuid': meeting['tenant_uuid'], f'user_uuid:{my_uuid}': True}
        s.check_event(
            'meeting_user_progress',
            headers,
            bus.BusClient.send_meeting_reload_complete_event,
            mine,
        )


@fixtures.ingress_http()
@fixtures.meeting()
@fixtures.meeting()
@fixtures.meeting(persistent=True)
def test_purge_old_meetings(_, meeting_too_old, meeting_too_young, meeting_persistent):
    too_old = datetime.now(timezone.utc) - timedelta(hours=25)
    with db.queries() as queries:
        queries.set_meeting_creation_date(meeting_too_old['uuid'], too_old)
        queries.set_meeting_creation_date(meeting_persistent['uuid'], too_old)

    BaseIntegrationTest.purge_meetings()

    response = confd.meetings(meeting_too_old['uuid']).get()
    response.assert_status(404)
    response = confd.meetings(meeting_too_young['uuid']).get()
    response.assert_status(200)
    response = confd.meetings(meeting_persistent['uuid']).get()
    response.assert_status(200)
