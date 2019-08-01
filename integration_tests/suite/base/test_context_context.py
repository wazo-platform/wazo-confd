# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    empty,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    fixtures,
    scenarios as s,
)

FAKE_ID = 999999999


def test_associate_errors():
    with fixtures.context() as context:
        response = confd.contexts(FAKE_ID).contexts.put(contexts=[context])
        response.assert_status(404)

        url = confd.contexts(context['id']).contexts().put
        error_checks(url)



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


def test_associate():
    with fixtures.context() as context, fixtures.context() as sub_context:
        response = confd.contexts(context['id']).contexts().put(contexts=[sub_context])
        response.assert_updated()



def test_associate_multiple():
    with fixtures.context() as context, fixtures.context() as sub_context1, fixtures.context() as sub_context2, fixtures.context() as sub_context3:
        response = confd.contexts(context['id']).contexts.put(
            contexts=[sub_context2, sub_context3, sub_context1]
        )
        response.assert_updated()

        response = confd.contexts(context['id']).get()
        assert_that(response.item, has_entries(
            contexts=contains(
                has_entries(id=sub_context2['id']),
                has_entries(id=sub_context3['id']),
                has_entries(id=sub_context1['id']),
            )
        ))



def test_associate_same_sub_context():
    with fixtures.context() as context, fixtures.context() as sub_context:
        contexts = [{'id': sub_context['id']}, {'id': sub_context['id']}]
        response = confd.contexts(context['id']).contexts.put(contexts=contexts)
        response.assert_status(400)



def test_associate_same_context():
    with fixtures.context() as context:
        contexts = [{'id': context['id']}]
        response = confd.contexts(context['id']).contexts.put(contexts=contexts)
        response.assert_status(400)



def test_get_contexts_associated_to_context():
    with fixtures.context() as context, fixtures.context() as sub_context1, fixtures.context() as sub_context2:
        with a.context_context(context, sub_context2, sub_context1):
            response = confd.contexts(context['id']).get()
            assert_that(response.item, has_entries(
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
            ))


def test_dissociate():
    with fixtures.context() as context, fixtures.context() as sub_context1, fixtures.context() as sub_context2:
        with a.context_context(context, sub_context1, sub_context2):
            response = confd.contexts(context['id']).contexts.put(contexts=[])
            response.assert_updated()


def test_delete_context_when_context_and_sub_context_associated():
    with fixtures.context() as context, fixtures.context() as sub_context1, fixtures.context() as sub_context2:
        with a.context_context(context, sub_context1, sub_context2, check=False):
            confd.contexts(context['id']).delete().assert_deleted()

            deleted_context = confd.contexts(context['id']).get
            s.check_resource_not_found(deleted_context, 'Context')


def test_delete_sub_context_when_context_and_sub_context_associated():
    with fixtures.context() as context1, fixtures.context() as context2, fixtures.context() as sub_context:
        with a.context_context(context1, sub_context, check=False), a.context_context(context2, sub_context, check=False):
            confd.contexts(sub_context['id']).delete().assert_deleted()

            deleted_sub_context = confd.contexts(sub_context['id']).get
            s.check_resource_not_found(deleted_sub_context, 'Context')

            response = confd.contexts(context1['id']).get()
            assert_that(response.item['contexts'], empty())

            response = confd.contexts(context2['id']).get()
            assert_that(response.item['contexts'], empty())
