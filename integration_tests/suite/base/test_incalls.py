# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains_inanyorder,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.helpers.destination import (
    invalid_destinations,
    valid_destinations,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)


def test_get_errors():
    fake_incall = confd.incalls(999999).get
    s.check_resource_not_found(fake_incall, 'Incall')


def test_delete_errors():
    fake_incall = confd.incalls(999999).delete
    s.check_resource_not_found(fake_incall, 'Incall')


def test_post_errors():
    url = confd.incalls.post
    error_checks(url)


def test_put_errors():
    with fixtures.incall() as incall:
        url = confd.incalls(incall['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', 123)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', s.random_string(40))
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', [])
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', {})
    s.check_bogus_field_returns_error(url, 'caller_id_mode', True)
    s.check_bogus_field_returns_error(url, 'caller_id_mode', 'invalid')
    s.check_bogus_field_returns_error(url, 'caller_id_mode', 1234)
    s.check_bogus_field_returns_error(url, 'caller_id_mode', [])
    s.check_bogus_field_returns_error(url, 'caller_id_mode', {})
    s.check_bogus_field_returns_error(url, 'caller_id_name', 1234)
    s.check_bogus_field_returns_error(url, 'caller_id_name', True)
    s.check_bogus_field_returns_error(url, 'caller_id_name', s.random_string(81))
    s.check_bogus_field_returns_error(url, 'caller_id_name', [])
    s.check_bogus_field_returns_error(url, 'caller_id_name', {})
    s.check_bogus_field_returns_error(url, 'description', 1234)
    s.check_bogus_field_returns_error(url, 'description', [])
    s.check_bogus_field_returns_error(url, 'destination', {})
    s.check_bogus_field_returns_error(url, 'destination', None)

    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'destination', destination)


def test_search():
    with fixtures.incall(description='search') as incall, fixtures.incall(description='hidden') as hidden:
        url = confd.incalls
        searches = {'description': 'search'}

        for field, term in searches.items():
            check_search(url, incall, hidden, field, term)



def check_search(url, incall, hidden, field, term):
    response = url.get(search=term)
    assert_that(
        response.items,
        all_of(
            has_item(has_entry(field, incall[field])),
            is_not(has_item(has_entry(field, hidden[field]))),
        ))

    response = url.get(**{field: incall[field]})
    assert_that(
        response.items,
        all_of(
            has_item(has_entry('id', incall['id'])),
            is_not(has_item(has_entry('id', hidden['id']))),
        )
    )


def test_search_multi_tenant():
    with fixtures.incall(wazo_tenant=MAIN_TENANT) as main, fixtures.incall(wazo_tenant=SUB_TENANT) as sub:
        response = confd.incalls.get(wazo_tenant=MAIN_TENANT)
        assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

        response = confd.incalls.get(wazo_tenant=SUB_TENANT)
        assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

        response = confd.incalls.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(response.items, has_items(main, sub))



def test_sorting_offset_limit():
    with fixtures.incall(description='sort1') as incall1, fixtures.incall(description='sort2') as incall2:
        url = confd.incalls.get
        s.check_sorting(url, incall1, incall2, 'description', 'sort')

        s.check_offset(url, incall1, incall2, 'description', 'sort')
        s.check_offset_legacy(url, incall1, incall2, 'description', 'sort')

        s.check_limit(url, incall1, incall2, 'description', 'sort')



def test_get():
    with fixtures.incall() as incall:
        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(
            id=incall['id'],
            preprocess_subroutine=incall['preprocess_subroutine'],
            description=incall['description'],
            caller_id_mode=incall['caller_id_mode'],
            caller_id_name=incall['caller_id_name'],
            destination=incall['destination'],
            extensions=empty(),
        ))



def test_create_minimal_parameters():
    response = confd.incalls.post(destination={'type': 'none'})
    response.assert_created('incalls')

    assert_that(response.item, has_entries(id=not_(empty()), tenant_uuid=MAIN_TENANT))


def test_create_all_parameters():
    response = confd.incalls.post(
        preprocess_subroutine='default',
        description='description',
        caller_id_mode='prepend',
        caller_id_name='name_',
        destination={'type': 'none'},
        wazo_tenant=SUB_TENANT,
    )
    response.assert_created('incalls')

    assert_that(response.item, has_entries(
        preprocess_subroutine='default',
        description='description',
        caller_id_mode='prepend',
        caller_id_name='name_',
        destination={'type': 'none'},
        tenant_uuid=SUB_TENANT,
    ))


def test_edit_minimal_parameters():
    with fixtures.incall() as incall:
        response = confd.incalls(incall['id']).put()
        response.assert_updated()

        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(incall))



def test_edit_all_parameters():
    with fixtures.incall() as incall:
        parameters = {
            'destination': {'type': 'none'},
            'preprocess_subroutine': 'default',
            'caller_id_mode': 'append',
            'caller_id_name': '_name',
            'description': 'description',
        }

        response = confd.incalls(incall['id']).put(**parameters)
        response.assert_updated()

        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(parameters))



def test_edit_multi_tenant():
    with fixtures.incall(wazo_tenant=MAIN_TENANT) as main, fixtures.incall(wazo_tenant=SUB_TENANT) as sub:
        response = confd.incalls(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Incall'))

        response = confd.incalls(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_valid_destinations():

    with fixtures.incall() as incall, \
            fixtures.meetme() as meetme, \
            fixtures.ivr() as ivr, \
            fixtures.group() as group, \
            fixtures.outcall() as outcall, \
            fixtures.queue() as queue, \
            fixtures.switchboard() as switchboard, \
            fixtures.user() as user, \
            fixtures.voicemail() as voicemail, \
            fixtures.conference() as conference, \
            fixtures.skill_rule() as skill_rule, \
            fixtures.application() as application:

        destinations = (meetme, ivr, group, outcall, queue, switchboard, user,
                        voicemail, conference, skill_rule, application)
        for destination in valid_destinations(*destinations):
            create_incall_with_destination(destination)
            update_incall_with_destination(incall['id'], destination)


def create_incall_with_destination(destination):
    response = confd.incalls.post(destination=destination)
    response.assert_created('incalls')
    assert_that(response.item, has_entries(destination=has_entries(**destination)))


def update_incall_with_destination(incall_id, destination):
    response = confd.incalls(incall_id).put(destination=destination)
    response.assert_updated()
    response = confd.incalls(incall_id).get()
    assert_that(response.item, has_entries(destination=has_entries(**destination)))


def test_delete():
    with fixtures.incall() as incall:
        response = confd.incalls(incall['id']).delete()
        response.assert_deleted()
        response = confd.incalls(incall['id']).get()
        response.assert_match(404, e.not_found(resource='Incall'))



def test_delete_multi_tenant():
    with fixtures.incall(wazo_tenant=MAIN_TENANT) as main, fixtures.incall(wazo_tenant=SUB_TENANT) as sub:
        response = confd.incalls(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Incall'))

        response = confd.incalls(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()



def test_get_group_destination_relation():
    with fixtures.group() as group:
        incall = confd.incalls.post(destination={'type': 'group',
                                                 'group_id': group['id']}).item

        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(
            destination=has_entries(group_id=group['id'], group_name=group['name'])
        ))



def test_get_user_destination_relation():
    with fixtures.user() as user:
        incall = confd.incalls.post(destination={'type': 'user',
                                                 'user_id': user['id']}).item

        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(
            destination=has_entries(
                user_id=user['id'],
                user_firstname=user['firstname'],
                user_lastname=user['lastname'],
            )
        ))



def test_get_ivr_destination_relation():
    with fixtures.ivr() as ivr:
        incall = confd.incalls.post(destination={'type': 'ivr',
                                                 'ivr_id': ivr['id']}).item

        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(
            destination=has_entries(ivr_id=ivr['id'], ivr_name=ivr['name'])
        ))



def test_get_conference_destination_relation():
    with fixtures.conference() as conference:
        incall = confd.incalls.post(destination={'type': 'conference',
                                                 'conference_id': conference['id']}).item

        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(
            destination=has_entries(conference_id=conference['id'], conference_name=conference['name'])
        ))



def test_get_switchboard_destination_relation():
    with fixtures.switchboard() as switchboard:
        incall = confd.incalls.post(destination={'type': 'switchboard',
                                                 'switchboard_uuid': switchboard['uuid']}).item

        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(
            destination=has_entries(switchboard_uuid=switchboard['uuid'], switchboard_name=switchboard['name'])
        ))



def test_get_voicemail_destination_relation():
    with fixtures.voicemail() as voicemail:
        incall = confd.incalls.post(destination={'type': 'voicemail',
                                                 'voicemail_id': voicemail['id']}).item

        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(
            destination=has_entries(voicemail_id=voicemail['id'], voicemail_name=voicemail['name'])
        ))



def test_get_queue_destination_relation():
    with fixtures.queue() as queue:
        incall = confd.incalls.post(destination={'type': 'queue', 'queue_id': queue['id']}).item

        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(
            destination=has_entries(
                queue_id=queue['id'],
                queue_label=queue['label'],
            )
        ))



def test_get_incalls_relation_when_group_destination():
    with fixtures.group() as group:
        incall1 = confd.incalls.post(destination={'type': 'group', 'group_id': group['id']}).item
        incall2 = confd.incalls.post(destination={'type': 'group', 'group_id': group['id']}).item

        response = confd.groups(group['id']).get()
        assert_that(response.item, has_entries(
            incalls=contains_inanyorder(
                has_entries(id=incall1['id'], extensions=incall1['extensions']),
                has_entries(id=incall2['id'], extensions=incall2['extensions']),
            )
        ))



def test_get_incalls_relation_when_user_destination():
    with fixtures.user() as user:
        incall1 = confd.incalls.post(destination={'type': 'user', 'user_id': user['id']}).item
        incall2 = confd.incalls.post(destination={'type': 'user', 'user_id': user['id']}).item

        response = confd.users(user['uuid']).get()
        assert_that(response.item, has_entries(
            incalls=contains_inanyorder(
                has_entries(id=incall1['id'], extensions=incall1['extensions']),
                has_entries(id=incall2['id'], extensions=incall2['extensions']),
            )
        ))



def test_get_incalls_relation_when_ivr_destination():
    with fixtures.ivr() as ivr:
        incall1 = confd.incalls.post(destination={'type': 'ivr', 'ivr_id': ivr['id']}).item
        incall2 = confd.incalls.post(destination={'type': 'ivr', 'ivr_id': ivr['id']}).item

        response = confd.ivr(ivr['id']).get()
        assert_that(response.item, has_entries(
            incalls=contains_inanyorder(
                has_entries(id=incall1['id'], extensions=incall1['extensions']),
                has_entries(id=incall2['id'], extensions=incall2['extensions']),
            )
        ))



def test_get_incalls_relation_when_conference_destination():
    with fixtures.conference() as conference:
        incall1 = confd.incalls.post(destination={'type': 'conference', 'conference_id': conference['id']}).item
        incall2 = confd.incalls.post(destination={'type': 'conference', 'conference_id': conference['id']}).item

        response = confd.conferences(conference['id']).get()
        assert_that(response.item, has_entries(
            incalls=contains_inanyorder(
                has_entries(id=incall1['id'], extensions=incall1['extensions']),
                has_entries(id=incall2['id'], extensions=incall2['extensions']),
            )
        ))



def test_get_incalls_relation_when_switchboard_destination():
    with fixtures.switchboard() as switchboard:
        incall1 = confd.incalls.post(destination={'type': 'switchboard', 'switchboard_uuid': switchboard['uuid']}).item
        incall2 = confd.incalls.post(destination={'type': 'switchboard', 'switchboard_uuid': switchboard['uuid']}).item

        response = confd.switchboards(switchboard['uuid']).get()
        assert_that(response.item, has_entries(
            incalls=contains_inanyorder(
                has_entries(id=incall1['id'], extensions=incall1['extensions']),
                has_entries(id=incall2['id'], extensions=incall2['extensions']),
            )
        ))

