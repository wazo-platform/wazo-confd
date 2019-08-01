# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
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


def test_associate_errors():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten()) as extension:
        fake_conference = confd.conferences(FAKE_ID).extensions(extension['id']).put
        fake_extension = confd.conferences(conference['id']).extensions(FAKE_ID).put

        s.check_resource_not_found(fake_conference, 'Conference')
        s.check_resource_not_found(fake_extension, 'Extension')



def test_dissociate_errors():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten()) as extension:
        fake_conference = confd.conferences(FAKE_ID).extensions(extension['id']).delete
        fake_extension = confd.conferences(conference['id']).extensions(FAKE_ID).delete

        s.check_resource_not_found(fake_conference, 'Conference')
        s.check_resource_not_found(fake_extension, 'Extension')



def test_associate():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten()) as extension:
        response = confd.conferences(conference['id']).extensions(extension['id']).put()
        response.assert_updated()



def test_associate_multi_tenant():
    with fixtures.conference(wazo_tenant=MAIN_TENANT) as main, fixtures.conference(wazo_tenant=SUB_TENANT) as sub, fixtures.context(
    wazo_tenant=MAIN_TENANT,
    name='main-internal',
    conference_room_ranges=[{'start': '4000', 'end': '4999'}],
) as _, fixtures.context(
    wazo_tenant=SUB_TENANT,
    name='sub-internal',
    conference_room_ranges=[{'start': '4000', 'end': '4999'}],
) as __, fixtures.extension(context='main-internal', exten=gen_conference_exten()) as main_exten, fixtures.extension(context='sub-internal', exten=gen_conference_exten()) as sub_exten:
        response = confd.conferences(sub['id']).extensions(main_exten['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.conferences(main['id']).extensions(sub_exten['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Conference'))

        response = confd.conferences(main['id']).extensions(sub_exten['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_associate_already_associated():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten()) as extension:
        with a.conference_extension(conference, extension):
            response = confd.conferences(conference['id']).extensions(extension['id']).put()
            response.assert_updated()


def test_associate_multiple_extensions_to_conference():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten()) as extension1, fixtures.extension(exten=gen_conference_exten()) as extension2:
        with a.conference_extension(conference, extension1):
            response = confd.conferences(conference['id']).extensions(extension2['id']).put()
            response.assert_match(400, e.resource_associated('Conference', 'Extension'))


def test_associate_multiple_conferences_to_extension():
    with fixtures.conference() as conference1, fixtures.conference() as conference2, fixtures.extension(exten=gen_conference_exten()) as extension:
        with a.conference_extension(conference1, extension):
            response = confd.conferences(conference2['id']).extensions(extension['id']).put()
            response.assert_match(400, e.resource_associated('Conference', 'Extension'))


def test_associate_when_user_already_associated():
    with fixtures.conference() as conference, fixtures.user() as user, fixtures.line_sip() as line_sip, fixtures.extension() as extension:
        with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
            response = confd.conferences(conference['id']).extensions(extension['id']).put()
            response.assert_match(400, e.resource_associated('user', 'Extension'))


def test_associate_when_not_internal_context():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten(), context=INCALL_CONTEXT) as extension:
        response = confd.conferences(conference['id']).extensions(extension['id']).put()
        response.assert_status(400)



def test_associate_when_exten_outside_range():
    with fixtures.conference() as conference, fixtures.extension(exten=EXTEN_OUTSIDE_RANGE) as extension:
        response = confd.conferences(conference['id']).extensions(extension['id']).put()
        response.assert_status(400)



def test_associate_when_exten_pattern():
    with fixtures.conference() as conference, fixtures.extension(exten='_1234') as extension:
        response = confd.conferences(conference['id']).extensions(extension['id']).put()
        response.assert_updated()



def test_dissociate():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten()) as extension:
        with a.conference_extension(conference, extension, check=False):
            response = confd.conferences(conference['id']).extensions(extension['id']).delete()
            response.assert_deleted()


def test_dissociate_multi_tenant():
    with fixtures.conference(wazo_tenant=MAIN_TENANT) as main, fixtures.conference(wazo_tenant=SUB_TENANT) as sub, fixtures.context(
    wazo_tenant=MAIN_TENANT,
    name='main-internal',
    conference_room_ranges=[{'start': '4000', 'end': '4999'}],
) as _, fixtures.context(
    wazo_tenant=SUB_TENANT,
    name='sub-internal',
    conference_room_ranges=[{'start': '4000', 'end': '4999'}],
) as __, fixtures.extension(context='main-internal', exten=gen_conference_exten()) as main_exten, fixtures.extension(context='sub-internal', exten=gen_conference_exten()) as sub_exten:
        response = confd.conferences(sub['id']).extensions(main_exten['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.conferences(main['id']).extensions(sub_exten['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Conference'))



def test_dissociate_not_associated():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten()) as extension:
        response = confd.conferences(conference['id']).extensions(extension['id']).delete()
        response.assert_deleted()



def test_get_conference_relation():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten()) as extension:
        with a.conference_extension(conference, extension):
            response = confd.conferences(conference['id']).get()
            assert_that(response.item, has_entries(
                extensions=contains(has_entries(id=extension['id'],
                                                exten=extension['exten'],
                                                context=extension['context']))
            ))


def test_get_extension_relation():
    with fixtures.extension(exten=gen_conference_exten()) as extension, fixtures.conference() as conference:
        with a.conference_extension(conference, extension):
            response = confd.extensions(extension['id']).get()
            assert_that(response.item, has_entries(
                conference=has_entries(id=conference['id'],
                                       name=conference['name'])
            ))


def test_edit_context_to_incall_when_associated():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten()) as extension:
        with a.conference_extension(conference, extension):
            response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
            response.assert_status(400)


def test_delete_conference_when_conference_and_extension_associated():
    with fixtures.conference() as conference, fixtures.extension(exten=gen_conference_exten()) as extension:
        with a.conference_extension(conference, extension, check=False):
            response = confd.conferences(conference['id']).delete()
            response.assert_deleted()


def test_delete_extension_when_conference_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
