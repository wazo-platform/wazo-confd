# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
    not_none,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd


def test_get_errors():
    fake_skill = confd.queues.skillrules(999999).get
    s.check_resource_not_found(fake_skill, 'SkillRule')


def test_delete_errors():
    fake_skill = confd.queues.skillrules(999999).delete
    s.check_resource_not_found(fake_skill, 'SkillRule')


def test_post_errors():
    url = confd.queues.skillrules
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')


@fixtures.skill_rule()
def test_put_errors(skill):
    url = confd.queues.skillrules(skill['id'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', 1234)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(65))
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'rules', True)
    s.check_bogus_field_returns_error(url, 'rules', 1234)
    s.check_bogus_field_returns_error(url, 'rules', {})
    s.check_bogus_field_returns_error(url, 'rules', 'string')
    s.check_bogus_field_returns_error(url, 'rules', ['string'])
    s.check_bogus_field_returns_error(url, 'rules', [{}])

    regex = r'rules.*definition'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'rules', [{'definition': True}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'rules', [{'definition': 1234}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'rules', [{'definition': []}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'rules', [{'definition': {}}], regex
    )


@fixtures.skill_rule(name='search')
@fixtures.skill_rule(name='hidden')
def test_search(skill, hidden):
    url = confd.queues.skillrules
    searches = {'name': 'search'}

    for field, term in searches.items():
        check_search(url, skill, hidden, field, term)


def check_search(url, skill, hidden, field, term):
    response = url.get(search=term)

    assert_that(response.items, has_item(has_entry(field, skill[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: skill[field]})

    assert_that(response.items, has_item(has_entry('id', skill['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.skill_rule(wazo_tenant=MAIN_TENANT)
@fixtures.skill_rule(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.queues.skillrules.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(
            has_item(has_entry('id', main['id'])),
            not_(has_item(has_entry('id', sub['id']))),
        ),
    )

    response = confd.queues.skillrules.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(
            has_item(has_entry('id', sub['id'])),
            not_(has_item(has_entry('id', main['id']))),
        ),
    )

    response = confd.queues.skillrules.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(has_entry('id', main['id']), has_entry('id', sub['id'])),
    )


@fixtures.skill_rule(name='sort1')
@fixtures.skill_rule(name='sort2')
def test_sort_offset_limit(skill1, skill2):
    url = confd.queues.skillrules.get
    s.check_sorting(url, skill1, skill2, 'name', 'sort')
    s.check_offset(url, skill1, skill2, 'name', 'sort')
    s.check_limit(url, skill1, skill2, 'name', 'sort')


@fixtures.skill_rule()
def test_get(skill_rule):
    response = confd.queues.skillrules(skill_rule['id']).get()
    assert_that(
        response.item,
        has_entries(id=skill_rule['id'], name=skill_rule['name'], rules=empty()),
    )


@fixtures.skill_rule(wazo_tenant=MAIN_TENANT)
@fixtures.skill_rule(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.queues.skillrules(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SkillRule'))

    response = confd.queues.skillrules(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(id=sub['id']))


def test_create_minimal_parameters():
    response = confd.queues.skillrules.post(name='MySkillRule')
    response.assert_created('skillrules')

    assert_that(response.item, has_entries(id=not_none()))

    confd.queues.skillrules(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MySkillRule',
        'rules': [
            {'definition': 'asterisk rule definition'},
            {'definition': 'another rule definition'},
        ],
    }

    response = confd.queues.skillrules.post(**parameters)
    response.assert_created('skillrules')
    response = confd.queues.skillrules(response.item['id']).get()

    assert_that(response.item, has_entries(parameters))

    confd.queues.skillrules(response.item['id']).delete().assert_deleted()


def test_create_multi_tenant():
    response = confd.queues.skillrules.post(name='MySkillRule', wazo_tenant=SUB_TENANT)
    response.assert_created('skillrules')

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))


@fixtures.skill_rule()
def test_edit_minimal_parameters(skill_rule):
    response = confd.queues.skillrules(skill_rule['id']).put()
    response.assert_updated()


@fixtures.skill_rule()
def test_edit_all_parameters(skill_rule):
    parameters = {
        'name': 'UpdatedSkillRule',
        'rules': [
            {'definition': 'updated rule definition'},
            {'definition': 'another rule definition'},
        ],
    }

    response = confd.queues.skillrules(skill_rule['id']).put(**parameters)
    response.assert_updated()

    response = confd.queues.skillrules(skill_rule['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.skill_rule(wazo_tenant=MAIN_TENANT)
@fixtures.skill_rule(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.queues.skillrules(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SkillRule'))

    response = confd.queues.skillrules(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.skill_rule()
def test_delete(skill_rule):
    response = confd.queues.skillrules(skill_rule['id']).delete()
    response.assert_deleted()
    response = confd.queues.skillrules(skill_rule['id']).get()
    response.assert_match(404, e.not_found(resource='SkillRule'))


@fixtures.skill_rule(wazo_tenant=MAIN_TENANT)
@fixtures.skill_rule(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.queues.skillrules(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SkillRule'))

    response = confd.queues.skillrules(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.skill_rule()
def test_bus_events(skill_rule):
    url = confd.queues.skillrules(skill_rule['id'])
    body = {'name': 'SkillRule'}
    headers = {'tenant_uuid': skill_rule['tenant_uuid']}

    s.check_event('skill_rule_created', headers, confd.queues.skillrules.post, body)
    s.check_event('skill_rule_edited', headers, url.put)
    s.check_event('skill_rule_deleted', headers, url.delete)
