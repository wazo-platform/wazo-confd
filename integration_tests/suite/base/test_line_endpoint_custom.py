# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    helpers as h,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)


@fixtures.line()
@fixtures.custom()
def test_associate_errors(line, custom):
    fake_line = confd.lines(999999999).endpoints.custom(custom['id']).put
    fake_custom = confd.lines(line['id']).endpoints.custom(999999999).put

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_custom, 'CustomEndpoint'


@fixtures.line()
@fixtures.custom()
def test_dissociate_errors(line, custom):
    fake_line = confd.lines(999999999).endpoints.custom(custom['id']).delete
    fake_custom = confd.lines(line['id']).endpoints.custom(999999999).delete

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_custom, 'CustomEndpoint'


def test_get_errors():
    fake_line = confd.lines(999999999).endpoints.custom.get
    fake_custom = confd.endpoints.custom(999999999).lines.get

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_custom, 'CustomEndpoint'


@fixtures.line()
@fixtures.custom()
def test_get_custom_endpoint_associated_to_line(line, custom):
    response = confd.lines(line['id']).endpoints.custom.get()
    response.assert_status(404)

    with a.line_endpoint_custom(line, custom):
        response = confd.lines(line['id']).endpoints.custom.get()
        assert_that(
            response.item,
            has_entries(
                line_id=line['id'],
                endpoint_id=custom['id'],
                endpoint='custom'
            )
        )


@fixtures.line()
@fixtures.custom()
def test_get_custom_endpoint_after_dissociation(line, custom):
    h.line_endpoint_custom.associate(line['id'], custom['id'])
    h.line_endpoint_custom.dissociate(line['id'], custom['id'])

    response = confd.lines(line['id']).endpoints.custom.get()
    response.assert_status(404)


@fixtures.line()
@fixtures.custom()
def test_get_line_associated_to_a_custom_endpoint(line, custom):
    response = confd.endpoints.custom(custom['id']).lines.get()
    response.assert_status(404)

    with a.line_endpoint_custom(line, custom):
        response = confd.endpoints.custom(custom['id']).lines.get()
        assert_that(
            response.item,
            has_entries(
                line_id=line['id'],
                endpoint_id=custom['id'],
                endpoint='custom'
            )
        )


@fixtures.line()
@fixtures.custom()
def test_associate(line, custom):
    response = confd.lines(line['id']).endpoints.custom(custom['id']).put()
    response.assert_updated()


@fixtures.line()
@fixtures.custom()
def test_associate_when_endpoint_already_associated(line, custom):
    with a.line_endpoint_custom(line, custom):
        response = confd.lines(line['id']).endpoints.custom(custom['id']).put()
        response.assert_updated()


@fixtures.line()
@fixtures.custom()
@fixtures.custom()
def test_associate_with_another_endpoint_when_already_associated(line, custom1, custom2):
    with a.line_endpoint_custom(line, custom1):
        response = confd.lines(line['id']).endpoints.custom(custom2['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.line()
@fixtures.custom()
def test_associate_multiple_lines_to_custom(line1, line2, custom):
    with a.line_endpoint_custom(line1, custom):
        response = confd.lines(line2['id']).endpoints.custom(custom['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.trunk()
@fixtures.custom()
def test_associate_when_trunk_already_associated(line, trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.lines(line['id']).endpoints.custom(custom['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line(context='main-internal')
@fixtures.line(context='sub-internal')
@fixtures.custom(wazo_tenant=MAIN_TENANT)
@fixtures.custom(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(_, __, main_line, sub_line, main_custom, sub_custom):
    response = confd.lines(main_line['id']).endpoints.custom(sub_custom['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Line'))

    response = confd.lines(sub_line['id']).endpoints.custom(main_custom['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('CustomEndpoint'))

    response = confd.lines(main_line['id']).endpoints.custom(sub_custom['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.line()
@fixtures.custom()
def test_dissociate(line, custom):
    with a.line_endpoint_custom(line, custom, check=False):
        response = confd.lines(line['id']).endpoints.custom(custom['id']).delete()
        response.assert_deleted()


@fixtures.line()
@fixtures.custom()
def test_dissociate_when_not_associated(line, custom):
    response = confd.lines(line['id']).endpoints.custom(custom['id']).delete()
    response.assert_deleted()


@fixtures.line()
@fixtures.custom()
@fixtures.user()
def test_dissociate_when_associated_to_user(line, custom, user):
    with a.line_endpoint_custom(line, custom), a.user_line(user, line):
        response = confd.lines(line['id']).endpoints.custom(custom['id']).delete()
        response.assert_match(400, e.resource_associated('Line', 'User'))


@fixtures.line()
@fixtures.custom()
@fixtures.extension()
def test_dissociate_when_associated_to_extension(line, custom, extension):
    with a.line_endpoint_custom(line, custom), a.line_extension(line, extension):
        response = confd.lines(line['id']).endpoints.custom(custom['id']).delete()
        response.assert_match(400, e.resource_associated('Line', 'Extension'))


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line(context='main-internal')
@fixtures.line(context='sub-internal')
@fixtures.custom(wazo_tenant=MAIN_TENANT)
@fixtures.custom(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(_, __, main_line, sub_line, main_custom, sub_custom):
    response = confd.lines(main_line['id']).endpoints.custom(sub_custom['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Line'))

    response = confd.lines(sub_line['id']).endpoints.custom(main_custom['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('CustomEndpoint'))


@fixtures.line()
@fixtures.custom()
def test_get_endpoint_custom_relation(line, custom):
    with a.line_endpoint_custom(line, custom):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item,
            has_entries(endpoint_custom=has_entries(
                id=custom['id'],
                interface=custom['interface'],
            ))
        )


@fixtures.line()
@fixtures.custom()
def test_get_line_relation(line, custom):
    with a.line_endpoint_custom(line, custom):
        response = confd.endpoints.custom(custom['id']).get()
        assert_that(
            response.item,
            has_entries(line=has_entries(id=line['id']))
        )


@fixtures.line()
@fixtures.custom()
def test_delete_endpoint_dissociates_line(line, custom):
    with a.line_endpoint_custom(line, custom, check=False):
        response = confd.endpoints.custom(custom['id']).delete()
        response.assert_deleted()

        response = confd.lines(line['id']).endpoints.custom.get()
        response.assert_status(404)
