# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      contains,
                      has_entries)
from ..helpers import scenarios as s
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import associations as a
from ..helpers.config import OUTCALL_CONTEXT, CONTEXT
from . import confd


FAKE_ID = 999999999


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_associate_errors(outcall, extension):
    fake_outcall = confd.outcalls(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.outcalls(outcall['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_outcall, 'Outcall'
    yield s.check_resource_not_found, fake_extension, 'Extension'

    url = confd.outcalls(outcall['id']).extensions(extension['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'caller_id', 123
    yield s.check_bogus_field_returns_error, url, 'caller_id', True
    yield s.check_bogus_field_returns_error, url, 'caller_id', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id', []
    yield s.check_bogus_field_returns_error, url, 'caller_id', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'external_prefix', s.random_string(65)
    yield s.check_bogus_field_returns_error, url, 'external_prefix', 'invalid_regex'
    yield s.check_bogus_field_returns_error, url, 'external_prefix', True
    yield s.check_bogus_field_returns_error, url, 'external_prefix', []
    yield s.check_bogus_field_returns_error, url, 'external_prefix', {}
    yield s.check_bogus_field_returns_error, url, 'prefix', s.random_string(33)
    yield s.check_bogus_field_returns_error, url, 'prefix', 'invalid_regex'
    yield s.check_bogus_field_returns_error, url, 'prefix', True
    yield s.check_bogus_field_returns_error, url, 'prefix', []
    yield s.check_bogus_field_returns_error, url, 'prefix', {}
    yield s.check_bogus_field_returns_error, url, 'strip_digits', None
    yield s.check_bogus_field_returns_error, url, 'strip_digits', 'string'
    yield s.check_bogus_field_returns_error, url, 'strip_digits', -1
    yield s.check_bogus_field_returns_error, url, 'strip_digits', []
    yield s.check_bogus_field_returns_error, url, 'strip_digits', {}


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_dissociate_errors(outcall, extension):
    fake_outcall = confd.outcalls(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.outcalls(outcall['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_outcall, 'Outcall'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_associate(outcall, extension):
    response = confd.outcalls(outcall['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_associate_with_all_parameters(outcall, extension):
    parameters = {'caller_id': 'CallerID',
                  'external_prefix': '418',
                  'prefix': '514',
                  'strip_digits': 5}
    response = confd.outcalls(outcall['id']).extensions(extension['id']).put(parameters)
    response.assert_updated()


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_associate_already_associated(outcall, extension):
    with a.outcall_extension(outcall, extension):
        response = confd.outcalls(outcall['id']).extensions(extension['id']).put(prefix='123')
        response.assert_updated()


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_associate_multiple_extensions_to_outcall(outcall, extension1, extension2):
    with a.outcall_extension(outcall, extension1):
        response = confd.outcalls(outcall['id']).extensions(extension2['id']).put()
        response.assert_updated()


@fixtures.outcall()
@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_associate_multiple_outcalls_to_extension(outcall1, outcall2, extension):
    with a.outcall_extension(outcall1, extension):
        response = confd.outcalls(outcall2['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('outcall', 'Extension'))


@fixtures.outcall()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_when_user_already_associated(outcall, user, line_sip, extension):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = confd.outcalls(outcall['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('user', 'Extension'))


@fixtures.outcall()
@fixtures.extension()
def test_associate_when_not_outcall_context(outcall, extension):
    response = confd.outcalls(outcall['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_dissociate(outcall, extension):
    with a.outcall_extension(outcall, extension, check=False):
        response = confd.outcalls(outcall['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_dissociate_not_associated(outcall, extension):
    response = confd.outcalls(outcall['id']).extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_get_outcall_relations(outcall, extension):
    expected = has_entries(
        extensions=contains(has_entries(id=extension['id'],
                                        exten=extension['exten'],
                                        context=extension['context'],
                                        external_prefix='123',
                                        prefix='456',
                                        strip_digits=2,
                                        caller_id='toto'))
    )

    with a.outcall_extension(outcall, extension,
                             external_prefix='123', prefix='456', strip_digits=2, caller_id='toto'):
        response = confd.outcalls(outcall['id']).get()
        assert_that(response.item, expected)


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_get_extension_relations(outcall, extension):
    expected = has_entries(
        outcall=has_entries(id=outcall['id'],
                            name=outcall['name'])
    )

    with a.outcall_extension(outcall, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(response.item, expected)


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_edit_context_to_internal_when_associated(outcall, extension):
    with a.outcall_extension(outcall, extension):
        response = confd.extensions(extension['id']).put(context=CONTEXT)
        response.assert_status(400)


@fixtures.outcall()
@fixtures.extension(context=OUTCALL_CONTEXT)
def test_delete_outcall_when_outcall_and_extension_associated(outcall, extension):
    with a.outcall_extension(outcall, extension, check=False):
        response = confd.outcalls(outcall['id']).delete()
        response.assert_deleted()


def test_delete_extension_when_outcall_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
