# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_exactly, empty, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT, SUB_TENANT2
from . import confd

FAKE_ID = 999999999


@fixtures.context()
def test_associate_errors(context):
    response = confd.contexts(FAKE_ID).contexts.put(contexts=[context])
    response.assert_status(404)

    url = confd.contexts(context['id']).contexts()
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'contexts', 123)
    s.check_bogus_field_returns_error(url, 'contexts', None)
    s.check_bogus_field_returns_error(url, 'contexts', True)
    s.check_bogus_field_returns_error(url, 'contexts', 'string')
    s.check_bogus_field_returns_error(url, 'contexts', [123])
    s.check_bogus_field_returns_error(url, 'contexts', [None])
    s.check_bogus_field_returns_error(url, 'contexts', ['string'])
    s.check_bogus_field_returns_error(url, 'contexts', [{}])
    s.check_bogus_field_returns_error(url, 'contexts', [{'id': None}])
    s.check_bogus_field_returns_error(url, 'contexts', [{'id': 'string'}])
    s.check_bogus_field_returns_error(url, 'contexts', [{'id': 1}, {'id': None}])
    s.check_bogus_field_returns_error(url, 'contexts', [{'not_id': 123}])
    s.check_bogus_field_returns_error(url, 'contexts', [{'id': FAKE_ID}])


@fixtures.context()
@fixtures.context()
def test_associate(context, sub_context):
    response = confd.contexts(context['id']).contexts().put(contexts=[sub_context])
    response.assert_updated()


@fixtures.context()
@fixtures.context()
@fixtures.context()
@fixtures.context()
def test_associate_multiple(context, sub_context1, sub_context2, sub_context3):
    response = confd.contexts(context['id']).contexts.put(
        contexts=[sub_context2, sub_context3, sub_context1]
    )
    response.assert_updated()

    response = confd.contexts(context['id']).get()
    assert_that(
        response.item,
        has_entries(
            contexts=contains_exactly(
                has_entries(id=sub_context2['id']),
                has_entries(id=sub_context3['id']),
                has_entries(id=sub_context1['id']),
            )
        ),
    )


@fixtures.context()
@fixtures.context()
def test_associate_same_sub_context(context, sub_context):
    contexts = [{'id': sub_context['id']}, {'id': sub_context['id']}]
    response = confd.contexts(context['id']).contexts.put(contexts=contexts)
    response.assert_status(400)


@fixtures.context()
def test_associate_same_context(context):
    contexts = [{'id': context['id']}]
    response = confd.contexts(context['id']).contexts.put(contexts=contexts)
    response.assert_status(400)


@fixtures.context()
@fixtures.context()
@fixtures.context()
def test_get_contexts_associated_to_context(context, sub_context1, sub_context2):
    with a.context_context(context, sub_context2, sub_context1):
        response = confd.contexts(context['id']).get()
        assert_that(
            response.item,
            has_entries(
                contexts=contains_exactly(
                    has_entries(
                        id=sub_context2['id'],
                        name=sub_context2['name'],
                        label=sub_context2['label'],
                    ),
                    has_entries(
                        id=sub_context1['id'],
                        name=sub_context1['name'],
                        label=sub_context1['label'],
                    ),
                )
            ),
        )


@fixtures.context()
@fixtures.context()
@fixtures.context()
def test_dissociate(context, sub_context1, sub_context2):
    with a.context_context(context, sub_context1, sub_context2):
        response = confd.contexts(context['id']).contexts.put(contexts=[])
        response.assert_updated()


@fixtures.context()
@fixtures.context()
@fixtures.context()
def test_delete_context_when_context_and_sub_context_associated(
    context, sub_context1, sub_context2
):
    with a.context_context(context, sub_context1, sub_context2, check=False):
        confd.contexts(context['id']).delete().assert_deleted()

        deleted_context = confd.contexts(context['id']).get
        s.check_resource_not_found(deleted_context, 'Context')


@fixtures.context()
@fixtures.context()
@fixtures.context()
def test_delete_sub_context_when_context_and_sub_context_associated(
    context1, context2, sub_context
):
    with a.context_context(context1, sub_context, check=False), a.context_context(
        context2, sub_context, check=False
    ):
        confd.contexts(sub_context['id']).delete().assert_deleted()

        deleted_sub_context = confd.contexts(sub_context['id']).get
        s.check_resource_not_found(deleted_sub_context, 'Context')

        response = confd.contexts(context1['id']).get()
        assert_that(response.item['contexts'], empty())

        response = confd.contexts(context2['id']).get()
        assert_that(response.item['contexts'], empty())


def put_contexts(context, contexts):
    def call(**kwargs):
        url = confd.contexts(context['id']).contexts()
        return url.put(contexts=contexts, **kwargs)

    return call


def included_context_ids(context):
    response = confd.contexts(context['id']).get()
    return [included['id'] for included in response.item['contexts']]


@fixtures.context(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT2)
def test_associate_context_outside_tenant(main_context, sub_context, sibling_context):
    for context in (main_context, sibling_context):
        call = put_contexts(context, [sub_context])
        s.check_outside_tenant_not_found(call, 'Context', SUB_TENANT)
        assert_that(included_context_ids(context), empty())


@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT)
def test_associate_sub_tenant_context_from_main_tenant(sub_context, sub_context2):
    call = put_contexts(sub_context, [sub_context2])
    s.check_sub_tenant_found(call, MAIN_TENANT, 204)
    assert_that(included_context_ids(sub_context), contains_exactly(sub_context2['id']))


@fixtures.context(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT2)
def test_associate_included_context_outside_tenant(
    main_context, sub_context, sub_context2, sibling_context
):
    put_contexts(sub_context, [sub_context2])(wazo_tenant=SUB_TENANT).assert_updated()

    for outside in (main_context, sibling_context):
        call = put_contexts(sub_context, [outside])
        response = call(wazo_tenant=SUB_TENANT)
        response.assert_match(400, e.not_found('Context'))
        assert_that(
            included_context_ids(sub_context),
            contains_exactly(sub_context2['id']),
        )


@fixtures.context(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT)
def test_associate_contexts_of_different_tenants(
    main_context, main_context2, sub_context
):
    call = put_contexts(main_context, [main_context2])
    call(wazo_tenant=MAIN_TENANT).assert_updated()

    response = put_contexts(main_context, [sub_context])(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())
    response = put_contexts(sub_context, [main_context2])(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())

    assert_that(
        included_context_ids(main_context), contains_exactly(main_context2['id'])
    )
    assert_that(included_context_ids(sub_context), empty())


@fixtures.context(wazo_tenant=SUB_TENANT2)
def test_associate_wazo_tenant_not_visible(sibling_context):
    s.check_wazo_tenant_not_visible_refused(put_contexts(sibling_context, []))
