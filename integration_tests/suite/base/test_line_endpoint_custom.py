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


def test_associate_errors():
    with fixtures.line() as line, fixtures.custom() as custom:
        fake_line = confd.lines(999999999).endpoints.custom(custom['id']).put
        fake_custom = confd.lines(line['id']).endpoints.custom(999999999).put

        s.check_resource_not_found(fake_line, 'Line')
        s.check_resource_not_found(fake_custom, 'CustomEndpoint')



def test_dissociate_errors():
    with fixtures.line() as line, fixtures.custom() as custom:
        fake_line = confd.lines(999999999).endpoints.custom(custom['id']).delete
        fake_custom = confd.lines(line['id']).endpoints.custom(999999999).delete

        s.check_resource_not_found(fake_line, 'Line')
        s.check_resource_not_found(fake_custom, 'CustomEndpoint')



def test_get_errors():
    fake_line = confd.lines(999999999).endpoints.custom.get
    fake_custom = confd.endpoints.custom(999999999).lines.get

    s.check_resource_not_found(fake_line, 'Line')
    s.check_resource_not_found(fake_custom, 'CustomEndpoint')


def test_get_custom_endpoint_associated_to_line():
    with fixtures.line() as line, fixtures.custom() as custom:
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



def test_get_custom_endpoint_after_dissociation():
    with fixtures.line() as line, fixtures.custom() as custom:
        h.line_endpoint_custom.associate(line['id'], custom['id'])
        h.line_endpoint_custom.dissociate(line['id'], custom['id'])

        response = confd.lines(line['id']).endpoints.custom.get()
        response.assert_status(404)



def test_get_line_associated_to_a_custom_endpoint():
    with fixtures.line() as line, fixtures.custom() as custom:
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



def test_associate():
    with fixtures.line() as line, fixtures.custom() as custom:
        response = confd.lines(line['id']).endpoints.custom(custom['id']).put()
        response.assert_updated()



def test_associate_when_endpoint_already_associated():
    with fixtures.line() as line, fixtures.custom() as custom:
        with a.line_endpoint_custom(line, custom):
            response = confd.lines(line['id']).endpoints.custom(custom['id']).put()
            response.assert_updated()


def test_associate_with_another_endpoint_when_already_associated():
    with fixtures.line() as line, fixtures.custom() as custom1, fixtures.custom() as custom2:
        with a.line_endpoint_custom(line, custom1):
            response = confd.lines(line['id']).endpoints.custom(custom2['id']).put()
            response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


def test_associate_multiple_lines_to_custom():
    with fixtures.line() as line1, fixtures.line() as line2, fixtures.custom() as custom:
        with a.line_endpoint_custom(line1, custom):
            response = confd.lines(line2['id']).endpoints.custom(custom['id']).put()
            response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


def test_associate_when_trunk_already_associated():
    with fixtures.line() as line, fixtures.trunk() as trunk, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk, custom):
            response = confd.lines(line['id']).endpoints.custom(custom['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


def test_associate_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as _, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as __, fixtures.line(context='main-internal') as main_line, fixtures.line(context='sub-internal') as sub_line, fixtures.custom(wazo_tenant=MAIN_TENANT) as main_custom, fixtures.custom(wazo_tenant=SUB_TENANT) as sub_custom:
        response = confd.lines(main_line['id']).endpoints.custom(sub_custom['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

        response = confd.lines(sub_line['id']).endpoints.custom(main_custom['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('CustomEndpoint'))

        response = confd.lines(main_line['id']).endpoints.custom(sub_custom['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.line() as line, fixtures.custom() as custom:
        with a.line_endpoint_custom(line, custom, check=False):
            response = confd.lines(line['id']).endpoints.custom(custom['id']).delete()
            response.assert_deleted()


def test_dissociate_when_not_associated():
    with fixtures.line() as line, fixtures.custom() as custom:
        response = confd.lines(line['id']).endpoints.custom(custom['id']).delete()
        response.assert_deleted()



def test_dissociate_when_associated_to_user():
    with fixtures.line() as line, fixtures.custom() as custom, fixtures.user() as user:
        with a.line_endpoint_custom(line, custom), a.user_line(user, line):
            response = confd.lines(line['id']).endpoints.custom(custom['id']).delete()
            response.assert_match(400, e.resource_associated('Line', 'User'))


def test_dissociate_when_associated_to_extension():
    with fixtures.line() as line, fixtures.custom() as custom, fixtures.extension() as extension:
        with a.line_endpoint_custom(line, custom), a.line_extension(line, extension):
            response = confd.lines(line['id']).endpoints.custom(custom['id']).delete()
            response.assert_match(400, e.resource_associated('Line', 'Extension'))


def test_dissociate_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as _, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as __, fixtures.line(context='main-internal') as main_line, fixtures.line(context='sub-internal') as sub_line, fixtures.custom(wazo_tenant=MAIN_TENANT) as main_custom, fixtures.custom(wazo_tenant=SUB_TENANT) as sub_custom:
        response = confd.lines(main_line['id']).endpoints.custom(sub_custom['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

        response = confd.lines(sub_line['id']).endpoints.custom(main_custom['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('CustomEndpoint'))



def test_get_endpoint_custom_relation():
    with fixtures.line() as line, fixtures.custom() as custom:
        with a.line_endpoint_custom(line, custom):
            response = confd.lines(line['id']).get()
            assert_that(
                response.item,
                has_entries(endpoint_custom=has_entries(
                    id=custom['id'],
                    interface=custom['interface'],
                ))
            )


def test_get_line_relation():
    with fixtures.line() as line, fixtures.custom() as custom:
        with a.line_endpoint_custom(line, custom):
            response = confd.endpoints.custom(custom['id']).get()
            assert_that(
                response.item,
                has_entries(line=has_entries(id=line['id']))
            )


def test_delete_endpoint_dissociates_line():
    with fixtures.line() as line, fixtures.custom() as custom:
        with a.line_endpoint_custom(line, custom, check=False):
            response = confd.endpoints.custom(custom['id']).delete()
            response.assert_deleted()

            response = confd.lines(line['id']).endpoints.custom.get()
            response.assert_status(404)
