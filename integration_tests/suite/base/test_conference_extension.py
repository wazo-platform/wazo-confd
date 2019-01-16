# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s
)
from ..helpers.config import (
    INCALL_CONTEXT,
    EXTEN_OUTSIDE_RANGE,
    gen_conference_exten,
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_ID = 999999999


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
def test_associate_errors(conference, extension):
    fake_conference = confd.conferences(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.conferences(conference['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_conference, 'Conference'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
def test_dissociate_errors(conference, extension):
    fake_conference = confd.conferences(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.conferences(conference['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_conference, 'Conference'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
def test_associate(conference, extension):
    response = confd.conferences(conference['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.conference(wazo_tenant=MAIN_TENANT)
@fixtures.conference(wazo_tenant=SUB_TENANT)
@fixtures.context(
    wazo_tenant=MAIN_TENANT,
    name='main-internal',
    conference_room_ranges=[{'start': '4000', 'end': '4999'}],
)
@fixtures.context(
    wazo_tenant=SUB_TENANT,
    name='sub-internal',
    conference_room_ranges=[{'start': '4000', 'end': '4999'}],
)
@fixtures.extension(context='main-internal', exten=gen_conference_exten())
@fixtures.extension(context='sub-internal', exten=gen_conference_exten())
def test_associate_multi_tenant(main, sub, _, __, main_exten, sub_exten):
    response = confd.conferences(sub['id']).extensions(main_exten['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Extension'))

    response = confd.conferences(main['id']).extensions(sub_exten['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Conference'))

    response = confd.conferences(main['id']).extensions(sub_exten['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
def test_associate_already_associated(conference, extension):
    with a.conference_extension(conference, extension):
        response = confd.conferences(conference['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
@fixtures.extension(exten=gen_conference_exten())
def test_associate_multiple_extensions_to_conference(conference, extension1, extension2):
    with a.conference_extension(conference, extension1):
        response = confd.conferences(conference['id']).extensions(extension2['id']).put()
        response.assert_match(400, e.resource_associated('Conference', 'Extension'))


@fixtures.conference()
@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
def test_associate_multiple_conferences_to_extension(conference1, conference2, extension):
    with a.conference_extension(conference1, extension):
        response = confd.conferences(conference2['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('Conference', 'Extension'))


@fixtures.conference()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_when_user_already_associated(conference, user, line_sip, extension):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = confd.conferences(conference['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('user', 'Extension'))


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten(), context=INCALL_CONTEXT)
def test_associate_when_not_internal_context(conference, extension):
    response = confd.conferences(conference['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.conference()
@fixtures.extension(exten=EXTEN_OUTSIDE_RANGE)
def test_associate_when_exten_outside_range(conference, extension):
    response = confd.conferences(conference['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.conference()
@fixtures.extension(exten='_1234')
def test_associate_when_exten_pattern(conference, extension):
    response = confd.conferences(conference['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
def test_dissociate(conference, extension):
    with a.conference_extension(conference, extension, check=False):
        response = confd.conferences(conference['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.conference(wazo_tenant=MAIN_TENANT)
@fixtures.conference(wazo_tenant=SUB_TENANT)
@fixtures.context(
    wazo_tenant=MAIN_TENANT,
    name='main-internal',
    conference_room_ranges=[{'start': '4000', 'end': '4999'}],
)
@fixtures.context(
    wazo_tenant=SUB_TENANT,
    name='sub-internal',
    conference_room_ranges=[{'start': '4000', 'end': '4999'}],
)
@fixtures.extension(context='main-internal', exten=gen_conference_exten())
@fixtures.extension(context='sub-internal', exten=gen_conference_exten())
def test_dissociate_multi_tenant(main, sub, _, __, main_exten, sub_exten):
    response = confd.conferences(sub['id']).extensions(main_exten['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Extension'))

    response = confd.conferences(main['id']).extensions(sub_exten['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Conference'))


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
def test_dissociate_not_associated(conference, extension):
    response = confd.conferences(conference['id']).extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
def test_get_conference_relation(conference, extension):
    with a.conference_extension(conference, extension):
        response = confd.conferences(conference['id']).get()
        assert_that(response.item, has_entries(
            extensions=contains(has_entries(id=extension['id'],
                                            exten=extension['exten'],
                                            context=extension['context']))
        ))


@fixtures.extension(exten=gen_conference_exten())
@fixtures.conference()
def test_get_extension_relation(extension, conference):
    with a.conference_extension(conference, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(response.item, has_entries(
            conference=has_entries(id=conference['id'],
                                   name=conference['name'])
        ))


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
def test_edit_context_to_incall_when_associated(conference, extension):
    with a.conference_extension(conference, extension):
        response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
        response.assert_status(400)


@fixtures.conference()
@fixtures.extension(exten=gen_conference_exten())
def test_delete_conference_when_conference_and_extension_associated(conference, extension):
    with a.conference_extension(conference, extension, check=False):
        response = confd.conferences(conference['id']).delete()
        response.assert_deleted()


def test_delete_extension_when_conference_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
