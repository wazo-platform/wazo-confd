# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
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

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)


def test_get_errors():
    fake_skill = confd.agents.skills(999999).get
    yield s.check_resource_not_found, fake_skill, 'Skill'


def test_delete_errors():
    fake_skill = confd.agents.skills(999999).delete
    yield s.check_resource_not_found, fake_skill, 'Skill'


def test_post_errors():
    url = confd.agents.skills.post
    for check in error_checks(url):
        yield check


@fixtures.skill()
def test_put_errors(skill):
    url = confd.agents.skills(skill['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', 'invalid regex'
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(65)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'category', True
    yield s.check_bogus_field_returns_error, url, 'category', 1234
    yield s.check_bogus_field_returns_error, url, 'category', s.random_string(65)
    yield s.check_bogus_field_returns_error, url, 'category', []
    yield s.check_bogus_field_returns_error, url, 'category', {}
    yield s.check_bogus_field_returns_error, url, 'description', True
    yield s.check_bogus_field_returns_error, url, 'description', 1234
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'description', {}

    for check in unique_error_checks(url):
        yield check


@fixtures.skill(name='unique')
def unique_error_checks(url, skill):
    yield s.check_bogus_field_returns_error, url, 'name', skill['name']


@fixtures.skill(name='search', category='search', description='search')
@fixtures.skill(name='hidden', category='hidden', description='hidden')
def test_search(skill, hidden):
    url = confd.agents.skills
    searches = {'name': 'search',
                'category': 'search',
                'description': 'search'}

    for field, term in searches.items():
        yield check_search, url, skill, hidden, field, term


def check_search(url, skill, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, skill[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: skill[field]})

    expected = has_item(has_entry('id', skill['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.skill(wazo_tenant=MAIN_TENANT)
@fixtures.skill(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.agents.skills.get(wazo_tenant=MAIN_TENANT)
    expected = all_of(
        has_item(has_entry('id', main['id'])),
        not_(has_item(has_entry('id', sub['id']))),
    )
    assert_that(response.items, expected)

    response = confd.agents.skills.get(wazo_tenant=SUB_TENANT)
    expected = all_of(
        has_item(has_entry('id', sub['id'])),
        not_(has_item(has_entry('id', main['id']))),
    )
    assert_that(response.items, expected)

    response = confd.agents.skills.get(wazo_tenant=MAIN_TENANT, recurse=True)
    expected = has_items(has_entry('id', main['id']), has_entry('id', sub['id']))
    assert_that(response.items, expected)


@fixtures.skill(name='sort1')
@fixtures.skill(name='sort2')
def test_sort_offset_limit(skill1, skill2):
    url = confd.agents.skills.get
    yield s.check_sorting, url, skill1, skill2, 'name', 'sort'

    yield s.check_offset, url, skill1, skill2, 'name', 'sort'
    yield s.check_offset_legacy, url, skill1, skill2, 'name', 'sort'

    yield s.check_limit, url, skill1, skill2, 'name', 'sort'


@fixtures.skill()
def test_get(skill):
    response = confd.agents.skills(skill['id']).get()
    assert_that(response.item, has_entries(
        id=skill['id'],
        name=skill['name'],
        category=skill['category'],
        description=skill['description'],

        agents=empty(),
    ))


@fixtures.skill(wazo_tenant=MAIN_TENANT)
@fixtures.skill(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.agents.skills(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Skill'))

    response = confd.agents.skills(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(id=sub['id']))


def test_create_minimal_parameters():
    response = confd.agents.skills.post(name='MySkill')
    response.assert_created('skills')

    assert_that(response.item, has_entries(id=not_none()))

    confd.agents.skills(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MySkill',
        'category': 'banana',
        'description': 'MyDescription',
    }

    response = confd.agents.skills.post(**parameters)
    response.assert_created('skills')
    response = confd.agents.skills(response.item['id']).get()

    assert_that(response.item, has_entries(parameters))

    confd.agents.skills(response.item['id']).delete().assert_deleted()


def test_create_multi_tenant():
    response = confd.agents.skills.post(name='MySkill', wazo_tenant=SUB_TENANT)
    response.assert_created('skill')

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))


@fixtures.skill()
def test_edit_minimal_parameters(skill):
    response = confd.agents.skills(skill['id']).put()
    response.assert_updated()


@fixtures.skill()
def test_edit_all_parameters(skill):
    parameters = {
        'name': 'UpdatedSkill',
        'category': 'UpdatedCategory',
        'description': 'UpdatedDescription',
    }

    response = confd.agents.skills(skill['id']).put(**parameters)
    response.assert_updated()

    response = confd.agents.skills(skill['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.skill(wazo_tenant=MAIN_TENANT)
@fixtures.skill(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.agents.skills(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Skill'))

    response = confd.agents.skills(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.skill()
def test_delete(skill):
    response = confd.agents.skills(skill['id']).delete()
    response.assert_deleted()
    response = confd.agents.skills(skill['id']).get()
    response.assert_match(404, e.not_found(resource='Skill'))


@fixtures.skill(wazo_tenant=MAIN_TENANT)
@fixtures.skill(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.agents.skills(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Skill'))

    response = confd.agents.skills(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.skill()
def test_bus_events(skill):
    required_body = {'name': 'Skill'}
    yield s.check_bus_event, 'config.agents.skills.created', confd.agents.skills.post, required_body
    yield s.check_bus_event, 'config.agents.skills.edited', confd.agents.skills(skill['id']).put
    yield s.check_bus_event, 'config.agents.skills.deleted', confd.agents.skills(skill['id']).delete
