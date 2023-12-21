# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from contextlib import ExitStack

from hamcrest import (
    assert_that,
    contains_inanyorder,
    has_entries,
    has_entry,
    has_item,
    is_not,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd


@fixtures.user()
def test_get_errors(user):
    fake_app = confd.users(user['uuid']).external.apps('invalid').get
    yield s.check_resource_not_found, fake_app, 'UserExternalApp'


@fixtures.user()
def test_delete_errors(user):
    fake_app = confd.users(user['uuid']).external.apps('invalid').delete
    yield s.check_resource_not_found, fake_app, 'UserExternalApp'


@fixtures.user_external_app(name='unique')
def test_post_errors(app):
    url = confd.users(app['user_uuid']).external.apps('myapp').post
    yield from error_checks(url)

    url = confd.users(app['user_uuid']).external.apps(s.random_string(129)).post
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)

    url = confd.users(app['user_uuid']).external.apps(app['name']).post
    yield s.check_bogus_field_returns_error, url, 'name', app['name']


@fixtures.user_external_app()
def test_put_errors(app):
    url = confd.users(app['user_uuid']).external.apps(app['name']).put
    yield from error_checks(url)


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'label', True
    yield s.check_bogus_field_returns_error, url, 'label', 1234
    yield s.check_bogus_field_returns_error, url, 'label', s.random_string(257)
    yield s.check_bogus_field_returns_error, url, 'label', []
    yield s.check_bogus_field_returns_error, url, 'label', {}
    yield s.check_bogus_field_returns_error, url, 'configuration', True
    yield s.check_bogus_field_returns_error, url, 'configuration', json.dumps('invalid')
    yield s.check_bogus_field_returns_error, url, 'configuration', json.dumps(1234)
    yield s.check_bogus_field_returns_error, url, 'configuration', []


@fixtures.user_external_app(wazo_tenant=MAIN_TENANT)
@fixtures.user_external_app(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.users(main['user_uuid']).external.apps.get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='User'))

    response = confd.users(sub['user_uuid']).external.apps.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items[0], has_entries(name=sub['name']))


@fixtures.user()
def test_search(user):
    with ExitStack() as es:
        external_app = es.enter_context(
            fixtures.user_external_app(user_uuid=user['uuid'], name='search')
        )
        hidden = es.enter_context(
            fixtures.user_external_app(user_uuid=user['uuid'], name='hidden')
        )

        url = confd.users(user['uuid']).external.apps
        searches = {'name': 'search'}

        for field, term in searches.items():
            yield check_search, url, external_app, hidden, field, term


def check_search(url, external_app, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, external_app[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: external_app[field]})
    assert_that(response.items, has_item(has_entry('name', external_app['name'])))
    assert_that(response.items, is_not(has_item(has_entry('name', hidden['name']))))


@fixtures.user()
def test_sort_offset_limit(user):
    with ExitStack() as es:
        external_app1 = es.enter_context(
            fixtures.user_external_app(user_uuid=user['uuid'], name='sort1')
        )
        external_app2 = es.enter_context(
            fixtures.user_external_app(user_uuid=user['uuid'], name='sort2')
        )

        url = confd.users(user['uuid']).external.apps.get
        yield s.check_sorting, url, external_app1, external_app2, 'name', 'sort', 'name'
        yield s.check_offset, url, external_app1, external_app2, 'name', 'sort', 'name'
        yield s.check_limit, url, external_app1, external_app2, 'name', 'sort', 'name'


@fixtures.user()
@fixtures.external_app(name='only-tenant')
@fixtures.external_app(name='both', label='from-tenant')
def test_list_with_fallback(user, *_):
    with ExitStack() as es:
        es.enter_context(
            fixtures.user_external_app(
                user_uuid=user['uuid'],
                name='both',
                label='from-user',
            )
        )
        es.enter_context(
            fixtures.user_external_app(
                user_uuid=user['uuid'],
                name='only-user',
            ),
        )

        response = confd.users(user['uuid']).external.apps.get(view='fallback')
        assert_that(
            response.items,
            contains_inanyorder(
                has_entries(name='only-tenant'),
                has_entries(name='only-user'),
                has_entries(name='both', label='from-user'),
            ),
        )


@fixtures.user_external_app()
def test_get(app):
    response = confd.users(app['user_uuid']).external.apps(app['name']).get()
    assert_that(
        response.item,
        has_entries(
            name=app['name'],
            label=app['label'],
            configuration=app['configuration'],
        ),
    )


@fixtures.user_external_app(wazo_tenant=MAIN_TENANT)
@fixtures.user_external_app(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = (
        confd.users(main['user_uuid'])
        .external.apps(main['name'])
        .get(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found(resource='User'))

    response = (
        confd.users(sub['user_uuid'])
        .external.apps(sub['name'])
        .get(wazo_tenant=MAIN_TENANT)
    )
    assert_that(response.item, has_entries(name=sub['name']))


@fixtures.user_external_app(name='both', label='from-user')
@fixtures.external_app(name='both', label='from-tenant')
def test_get_with_fallback(user_app, *_):
    user_uuid = user_app['user_uuid']
    response = confd.users(user_uuid).external.apps('both').get(view='fallback')
    assert_that(response.item, has_entries(name='both', label='from-user'))

    confd.users(user_uuid).external.apps('both').delete().assert_deleted()

    response = confd.users(user_uuid).external.apps('both').get(view='fallback')
    assert_that(response.item, has_entries(name='both', label='from-tenant'))

    confd.external.apps('both').delete().assert_deleted()

    response = confd.users(user_uuid).external.apps('both').get(view='fallback')
    response.assert_match(404, e.not_found(resource='UserExternalApp'))


@fixtures.user()
def test_create_minimal_parameters(user):
    response = confd.users(user['uuid']).external.apps('myapp').post()
    response.assert_status(201)

    assert_that(response.item, has_entries(name='myapp'))

    confd.users(user['uuid']).external.apps('myapp').delete().assert_deleted()


@fixtures.user()
def test_create_all_parameters(user):
    name = 'myapp'
    parameters = {
        'label': 'My app label',
        'configuration': {'key': {'subkey': 'value'}},
    }

    response = confd.users(user['uuid']).external.apps(name).post(**parameters)
    response.assert_status(201)
    response = confd.users(user['uuid']).external.apps(name).get()

    assert_that(response.item, has_entries(name=name, **parameters))

    confd.users(user['uuid']).external.apps(name).delete().assert_deleted()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_create_multi_tenant(main, sub):
    name = 'myapp'
    response = (
        confd.users(main['uuid']).external.apps(name).post(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found(resource='User'))

    response = (
        confd.users(sub['uuid']).external.apps(name).post(wazo_tenant=MAIN_TENANT)
    )
    assert_that(response.item, has_entries(name=name))

    confd.users(sub['uuid']).external.apps(name).delete().assert_deleted()


@fixtures.user_external_app()
def test_edit_minimal_parameters(app):
    response = confd.users(app['user_uuid']).external.apps(app['name']).put()
    response.assert_updated()


@fixtures.user_external_app()
def test_edit_all_parameters(app):
    parameters = {
        'label': 'My app label',
        'configuration': {'key': {'subkey': 'value'}},
    }

    response = (
        confd.users(app['user_uuid']).external.apps(app['name']).put(**parameters)
    )
    response.assert_updated()

    response = confd.users(app['user_uuid']).external.apps(app['name']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.user_external_app(wazo_tenant=MAIN_TENANT)
@fixtures.user_external_app(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = (
        confd.users(main['user_uuid'])
        .external.apps(main['name'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found(resource='User'))

    response = (
        confd.users(sub['user_uuid'])
        .external.apps(sub['name'])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_updated()


@fixtures.user_external_app()
def test_delete(app):
    response = confd.users(app['user_uuid']).external.apps(app['name']).delete()
    response.assert_deleted()
    response = confd.users(app['user_uuid']).external.apps(app['name']).get()
    response.assert_match(404, e.not_found(resource='UserExternalApp'))


@fixtures.user_external_app(wazo_tenant=MAIN_TENANT)
@fixtures.user_external_app(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = (
        confd.users(main['user_uuid'])
        .external.apps(main['name'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found(resource='User'))

    response = (
        confd.users(sub['user_uuid'])
        .external.apps(sub['name'])
        .delete(wazo_tenant=MAIN_TENANT)
    )
    response.assert_deleted()


@fixtures.user()
def test_bus_events(user):
    url = confd.users(user['uuid']).external.apps('myapp')
    headers = {'tenant_uuid': user['tenant_uuid']}

    yield s.check_event, 'user_external_app_created', headers, url.post
    yield s.check_event, 'user_external_app_edited', headers, url.put
    yield s.check_event, 'user_external_app_deleted', headers, url.delete
