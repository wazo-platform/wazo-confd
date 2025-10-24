# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from ..helpers.helpers.destination import invalid_destinations, valid_destinations
from . import confd


def test_get_errors():
    fake_schedule = confd.schedules(999999).get
    s.check_resource_not_found(fake_schedule, 'Schedule')


def test_delete_errors():
    fake_schedule = confd.schedules(999999).delete
    s.check_resource_not_found(fake_schedule, 'Schedule')


@fixtures.user()
def test_post_errors(user):
    url = confd.schedules
    error_checks(url.post, user)
    s.check_missing_body_returns_error(url, 'POST')


@fixtures.schedule()
@fixtures.user()
def test_put_errors(schedule, user):
    url = confd.schedules(schedule['id'])
    error_checks(url.put, user)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url, user):
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', 1234)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'timezone', True)
    s.check_bogus_field_returns_error(url, 'timezone', 1234)
    s.check_bogus_field_returns_error(url, 'timezone', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'timezone', [])
    s.check_bogus_field_returns_error(url, 'timezone', {})
    s.check_bogus_field_returns_error(url, 'enabled', 'invalid')
    s.check_bogus_field_returns_error(url, 'enabled', None)
    s.check_bogus_field_returns_error(url, 'enabled', [])
    s.check_bogus_field_returns_error(url, 'enabled', {})
    s.check_bogus_field_returns_error(url, 'open_periods', True)
    s.check_bogus_field_returns_error(url, 'open_periods', 1234)
    s.check_bogus_field_returns_error(url, 'open_periods', 'invalid')
    s.check_bogus_field_returns_error(url, 'open_periods', {})
    s.check_bogus_field_returns_error(url, 'exceptional_periods', True)
    s.check_bogus_field_returns_error(url, 'exceptional_periods', None)
    s.check_bogus_field_returns_error(url, 'exceptional_periods', 1234)
    s.check_bogus_field_returns_error(url, 'exceptional_periods', 'invalid')
    s.check_bogus_field_returns_error(url, 'exceptional_periods', {})

    for key in ('open_periods', 'exceptional_periods'):
        regex = r'{}.*0.*hours_start'.format(key)
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_start': 7}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_start': '7:15'}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_start': 'abcd'}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_start': None}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_start': '24:00'}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_start': '10:60'}], regex
        )

        regex = r'{}.*0.*hours_end'.format(key)
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_end': 8}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_end': '8:15'}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_end': 'abcd'}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_end': None}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_end': '24:00'}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'hours_end': '10:60'}], regex
        )

        regex = r'{}.*0.*week_days'.format(key)
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'week_days': None}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'week_days': 1}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'week_days': []}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'week_days': ['1-2']}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'week_days': [None]}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'week_days': [-1]}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'week_days': [8]}], regex
        )

        regex = r'{}.*0.*month_days'.format(key)
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'month_days': None}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'month_days': 1}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'month_days': []}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'month_days': ['1-2']}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'month_days': [None]}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'month_days': [-1]}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'month_days': [32]}], regex
        )

        regex = r'{}.*0.*months'.format(key)
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'months': None}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'months': 1}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'months': []}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'months': ['1-2']}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'months': [None]}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'months': [-1]}], regex
        )
        s.check_bogus_field_returns_error_matching_regex(
            url, key, [{'months': [13]}], regex
        )

    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'closed_destination', destination)
    s.check_bogus_field_returns_error(
        url,
        'closed_destination',
        {
            'type': 'user',
            'user_id': user['id'],
            'moh_uuid': '00000000-0000-0000-0000-000000000000',
        },
        {},
        'MOH was not found',
    )

    for destination in invalid_destinations():
        regex = r'exceptional_periods.*0.*destination'
        body = [{'destination': destination}]
        s.check_bogus_field_returns_error_matching_regex(
            url, 'exceptional_periods', body, regex
        )


@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.schedules.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.schedules.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.schedules.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.schedule(name='search', timezone='search')
@fixtures.schedule(name='hidden', timezone='hidden')
def test_search(schedule, hidden):
    url = confd.schedules
    searches = {'name': 'search', 'timezone': 'search'}

    for field, term in searches.items():
        check_search(url, schedule, hidden, field, term)


def check_search(url, schedule, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, schedule[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: schedule[field]})
    assert_that(response.items, has_item(has_entry('id', schedule['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.schedule(name='sort1')
@fixtures.schedule(name='sort2')
def test_sort_offset_limit(schedule1, schedule2):
    url = confd.schedules.get
    s.check_sorting(url, schedule1, schedule2, 'name', 'sort')

    s.check_offset(url, schedule1, schedule2, 'name', 'sort')
    s.check_limit(url, schedule1, schedule2, 'name', 'sort')


@fixtures.schedule()
def test_get(schedule):
    response = confd.schedules(schedule['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=schedule['id'],
            name=schedule['name'],
            timezone=schedule['timezone'],
            closed_destination=schedule['closed_destination'],
            open_periods=schedule['open_periods'],
            exceptional_periods=schedule['exceptional_periods'],
            enabled=schedule['enabled'],
            groups=empty(),
            incalls=empty(),
            outcalls=empty(),
            queues=empty(),
            users=empty(),
        ),
    )


@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.schedules(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Schedule'))

    response = confd.schedules(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.schedules.post(closed_destination={'type': 'none'})
    response.assert_created('schedules')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, id=not_(empty())))

    confd.schedules(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MySchedule',
        'timezone': 'American/Toronto',
        'closed_destination': {'type': 'hangup', 'cause': 'busy', 'timeout': 25},
        'open_periods': [
            {
                'hours_start': '07:15',
                'hours_end': '08:15',
                'week_days': [1, 2, 3, 4, 5],
                'month_days': [1, 15, 30],
                'months': [1, 6, 12],
            }
        ],
        'exceptional_periods': [
            {
                'hours_start': '07:25',
                'hours_end': '07:35',
                'week_days': [1, 2, 3, 4, 5],
                'month_days': [1, 30],
                'months': [1, 12],
                'destination': {'type': 'hangup', 'cause': 'congestion', 'timeout': 30},
            }
        ],
        'enabled': False,
    }

    response = confd.schedules.post(**parameters)
    response.assert_created('schedules')
    response = confd.schedules(response.item['id']).get()

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.schedules(response.item['id']).delete().assert_deleted()


def test_create_open_periods_default_values():
    response = confd.schedules.post(
        open_periods=[{'hours_start': '07:15', 'hours_end': '08:15'}],
        closed_destination={'type': 'none'},
    )

    assert_that(
        response.item,
        has_entries(
            open_periods=contains(
                has_entries(
                    hours_start='07:15',
                    hours_end='08:15',
                    week_days=[1, 2, 3, 4, 5, 6, 7],
                    month_days=[
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10,
                        11,
                        12,
                        13,
                        14,
                        15,
                        16,
                        17,
                        18,
                        19,
                        20,
                        21,
                        22,
                        23,
                        24,
                        25,
                        26,
                        27,
                        28,
                        29,
                        30,
                        31,
                    ],
                    months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                )
            )
        ),
    )

    confd.schedules(response.item['id']).delete().assert_deleted()


def test_create_exceptional_periods_default_values():
    response = confd.schedules.post(
        exceptional_periods=[
            {
                'hours_start': '07:15',
                'hours_end': '08:15',
                'destination': {'type': 'none'},
            }
        ],
        closed_destination={'type': 'none'},
    )

    assert_that(
        response.item,
        has_entries(
            exceptional_periods=contains(
                has_entries(
                    hours_start='07:15',
                    hours_end='08:15',
                    week_days=[1, 2, 3, 4, 5, 6, 7],
                    month_days=[
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10,
                        11,
                        12,
                        13,
                        14,
                        15,
                        16,
                        17,
                        18,
                        19,
                        20,
                        21,
                        22,
                        23,
                        24,
                        25,
                        26,
                        27,
                        28,
                        29,
                        30,
                        31,
                    ],
                    months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    destination={'type': 'none'},
                )
            )
        ),
    )

    confd.schedules(response.item['id']).delete().assert_deleted()


@fixtures.schedule()
def test_edit_minimal_parameters(schedule):
    response = confd.schedules(schedule['id']).put()
    response.assert_updated()


@fixtures.schedule()
def test_edit_all_parameters(schedule):
    parameters = {
        'name': 'MySchedule',
        'timezone': 'American/Toronto',
        'closed_destination': {'type': 'hangup', 'cause': 'busy', 'timeout': 25},
        'open_periods': [
            {
                'hours_start': '07:15',
                'hours_end': '08:15',
                'week_days': [1, 2, 3, 4, 5],
                'month_days': [1, 15, 30],
                'months': [1, 6, 12],
            }
        ],
        'exceptional_periods': [
            {
                'hours_start': '07:25',
                'hours_end': '07:35',
                'week_days': [1, 2, 3, 4, 5],
                'month_days': [1, 30],
                'months': [1, 12],
                'destination': {'type': 'hangup', 'cause': 'congestion', 'timeout': 30},
            }
        ],
        'enabled': False,
    }

    response = confd.schedules(schedule['id']).put(**parameters)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.schedule()
@fixtures.ivr()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.switchboard()
@fixtures.user()
@fixtures.voicemail()
@fixtures.conference()
@fixtures.skill_rule()
@fixtures.application()
@fixtures.moh()
def test_valid_destinations(schedule, *destinations):
    for destination in valid_destinations(*destinations):
        create_schedule_with_destination(destination)
        update_schedule_with_destination(schedule['id'], destination)


def create_schedule_with_destination(destination):
    response = confd.schedules.post(
        closed_destination=destination,
        exceptional_periods=[
            {'hours_start': '07:15', 'hours_end': '08:15', 'destination': destination}
        ],
    )
    response.assert_created('schedules')
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(**destination),
            exceptional_periods=has_items(
                has_entries(destination=has_entries(**destination))
            ),
        ),
    )

    confd.schedules(response.item['id']).delete().assert_deleted()


def update_schedule_with_destination(schedule_id, destination):
    response = confd.schedules(schedule_id).put(
        closed_destination=destination,
        exceptional_periods=[
            {'hours_start': '07:15', 'hours_end': '08:15', 'destination': destination}
        ],
    )
    response.assert_updated()
    response = confd.schedules(schedule_id).get()
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(**destination),
            exceptional_periods=has_items(
                has_entries(destination=has_entries(**destination))
            ),
        ),
    )


@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.schedules(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Schedule'))

    response = confd.schedules(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.schedule()
def test_delete(schedule):
    response = confd.schedules(schedule['id']).delete()
    response.assert_deleted()
    response = confd.schedules(schedule['id']).get()
    response.assert_match(404, e.not_found(resource='Schedule'))


@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.schedules(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Schedule'))

    response = confd.schedules(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.schedule()
def test_bus_events(schedule):
    url = confd.schedules(schedule['id'])
    body = {'closed_destination': {'type': 'none'}}
    headers = {'tenant_uuid': schedule['tenant_uuid']}

    s.check_event('schedule_created', headers, confd.schedules.post, body)
    s.check_event('schedule_edited', headers, url.put)
    s.check_event('schedule_deleted', headers, url.delete)


@fixtures.schedule()
@fixtures.group()
def test_get_group_destination_relation(schedule, group):
    destination = {'type': 'group', 'group_id': group['id']}
    response = confd.schedules(schedule['id']).put(closed_destination=destination)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(
                group_id=group['id'],
                group_name=group['name'],
                group_label=group['label'],
            ),
        ),
    )


@fixtures.schedule()
@fixtures.user()
def test_get_user_destination_relation(schedule, user):
    destination = {'type': 'user', 'user_id': user['id']}
    response = confd.schedules(schedule['id']).put(closed_destination=destination)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(
                user_id=user['id'],
                user_firstname=user['firstname'],
                user_lastname=user['lastname'],
            )
        ),
    )


@fixtures.schedule()
@fixtures.ivr()
def test_get_ivr_destination_relation(schedule, ivr):
    destination = {'type': 'ivr', 'ivr_id': ivr['id']}
    response = confd.schedules(schedule['id']).put(closed_destination=destination)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(
                ivr_id=ivr['id'],
                ivr_name=ivr['name'],
            )
        ),
    )


@fixtures.schedule()
@fixtures.conference(name='my-name')
def test_get_conference_destination_relation(schedule, conference):
    destination = {'type': 'conference', 'conference_id': conference['id']}
    response = confd.schedules(schedule['id']).put(closed_destination=destination)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(
                conference_id=conference['id'],
                conference_name=conference['name'],
            )
        ),
    )


@fixtures.schedule()
@fixtures.switchboard()
def test_get_switchboard_destination_relation(schedule, switchboard):
    destination = {'type': 'switchboard', 'switchboard_uuid': switchboard['uuid']}
    response = confd.schedules(schedule['id']).put(closed_destination=destination)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(
                switchboard_uuid=switchboard['uuid'],
                switchboard_name=switchboard['name'],
            )
        ),
    )


@fixtures.schedule()
@fixtures.voicemail()
def test_get_voicemail_destination_relation(schedule, voicemail):
    destination = {'type': 'voicemail', 'voicemail_id': voicemail['id']}
    response = confd.schedules(schedule['id']).put(closed_destination=destination)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(
                voicemail_id=voicemail['id'],
                voicemail_name=voicemail['name'],
            )
        ),
    )


@fixtures.schedule()
@fixtures.queue(label='hello-world')
def test_get_queue_destination_relation(schedule, queue):
    destination = {'type': 'queue', 'queue_id': queue['id']}
    response = confd.schedules(schedule['id']).put(closed_destination=destination)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(
                queue_id=queue['id'],
                queue_label=queue['label'],
            )
        ),
    )


@fixtures.schedule()
@fixtures.application(name='my-name')
def test_get_application_destination_relation(schedule, application):
    destination = {
        'type': 'application',
        'application': 'custom',
        'application_uuid': application['uuid'],
    }
    response = confd.schedules(schedule['id']).put(closed_destination=destination)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(
                application_uuid=application['uuid'],
                application_name=application['name'],
            )
        ),
    )


@fixtures.schedule()
@fixtures.application(name='my-name')
@fixtures.conference(name='my-name')
@fixtures.group()
@fixtures.ivr()
@fixtures.queue(label='hello-world')
@fixtures.switchboard()
@fixtures.user()
@fixtures.voicemail()
def test_get_exceptional_periods_destination_relations(
    schedule,
    application,
    conference,
    group,
    ivr,
    queue,
    switchboard,
    user,
    voicemail,
):
    destinations = [
        {
            'type': 'application',
            'application': 'custom',
            'application_uuid': application['uuid'],
        },
        {'type': 'conference', 'conference_id': conference['id']},
        {'type': 'group', 'group_id': group['id']},
        {'type': 'ivr', 'ivr_id': ivr['id']},
        {'type': 'queue', 'queue_id': queue['id']},
        {'type': 'switchboard', 'switchboard_uuid': switchboard['uuid']},
        {'type': 'user', 'user_id': user['id']},
        {'type': 'voicemail', 'voicemail_id': voicemail['id']},
    ]
    destinations_expected = [
        has_entries(
            application_uuid=application['uuid'],
            application_name=application['name'],
        ),
        has_entries(
            conference_id=conference['id'],
            conference_name=conference['name'],
        ),
        has_entries(
            group_id=group['id'],
            group_name=group['name'],
            group_label=group['label'],
        ),
        has_entries(
            ivr_id=ivr['id'],
            ivr_name=ivr['name'],
        ),
        has_entries(
            queue_id=queue['id'],
            queue_label=queue['label'],
        ),
        has_entries(
            switchboard_uuid=switchboard['uuid'],
            switchboard_name=switchboard['name'],
        ),
        has_entries(
            user_id=user['id'],
            user_firstname=user['firstname'],
            user_lastname=user['lastname'],
        ),
        has_entries(
            voicemail_id=voicemail['id'],
            voicemail_name=voicemail['name'],
        ),
    ]

    periods = []
    for i, destination in enumerate(destinations):
        periods.append(
            {
                'hours_start': f'{i:02d}:00',
                'hours_end': f'{i:02d}:59',
                'destination': destination,
            }
        )

    response = confd.schedules(schedule['id']).put(exceptional_periods=periods)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    expected = [has_entries(destination=dst) for dst in destinations_expected]
    assert_that(
        response.item,
        has_entries(exceptional_periods=contains_inanyorder(*expected)),
    )
