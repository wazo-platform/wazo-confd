# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, empty, has_entries

from . import confd
from ..helpers import associations as a, fixtures, scenarios as s

FAKE_ID = 999999999


@fixtures.context()
def test_associate_errors(context):
    response = confd.contexts(FAKE_ID).contexts.put(contexts=[context])
    response.assert_status(404)

    url = confd.contexts(context['id']).contexts().put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'contexts', 123
    yield s.check_bogus_field_returns_error, url, 'contexts', None
    yield s.check_bogus_field_returns_error, url, 'contexts', True
    yield s.check_bogus_field_returns_error, url, 'contexts', 'string'
    yield s.check_bogus_field_returns_error, url, 'contexts', [123]
    yield s.check_bogus_field_returns_error, url, 'contexts', [None]
    yield s.check_bogus_field_returns_error, url, 'contexts', ['string']
    yield s.check_bogus_field_returns_error, url, 'contexts', [{}]
    yield s.check_bogus_field_returns_error, url, 'contexts', [{'id': None}]
    yield s.check_bogus_field_returns_error, url, 'contexts', [{'id': 'string'}]
    yield s.check_bogus_field_returns_error, url, 'contexts', [{'id': 1}, {'id': None}]
    yield s.check_bogus_field_returns_error, url, 'contexts', [{'not_id': 123}]
    yield s.check_bogus_field_returns_error, url, 'contexts', [{'id': FAKE_ID}]


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
            contexts=contains(
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
                contexts=contains(
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
        yield s.check_resource_not_found, deleted_context, 'Context'


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
        yield s.check_resource_not_found, deleted_sub_context, 'Context'

        response = confd.contexts(context1['id']).get()
        yield assert_that, response.item['contexts'], empty()

        response = confd.contexts(context2['id']).get()
        yield assert_that, response.item['contexts'], empty()
