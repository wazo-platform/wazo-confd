# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
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
    with fixtures.line() as line, fixtures.sccp() as sccp:
        fake_line = confd.lines(999999999).endpoints.sccp(sccp['id']).put
        fake_sccp = confd.lines(line['id']).endpoints.sccp(999999999).put

        s.check_resource_not_found(fake_line, 'Line')
        s.check_resource_not_found(fake_sccp, 'SCCPEndpoint')



def test_dissociate_errors():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        fake_line = confd.lines(999999999).endpoints.sccp(sccp['id']).delete
        fake_sccp = confd.lines(line['id']).endpoints.sccp(999999999).delete

        s.check_resource_not_found(fake_line, 'Line')
        s.check_resource_not_found(fake_sccp, 'SCCPEndpoint')



def test_get_errors():
    fake_line = confd.lines(999999999).endpoints.sccp.get
    fake_sccp = confd.endpoints.sccp(999999999).lines.get

    s.check_resource_not_found(fake_line, 'Line')
    s.check_resource_not_found(fake_sccp, 'SCCPEndpoint')


def test_get_sccp_endpoint_associated_to_line():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        response = confd.lines(line['id']).endpoints.sccp.get()
        response.assert_status(404)

        with a.line_endpoint_sccp(line, sccp):
            response = confd.lines(line['id']).endpoints.sccp.get()
            assert_that(
                response.item,
                has_entries(
                    line_id=line['id'],
                    endpoint_id=sccp['id'],
                    endpoint='sccp'
                )
            )



def test_get_sccp_endpoint_after_dissociation():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        h.line_endpoint_sccp.associate(line['id'], sccp['id'])
        h.line_endpoint_sccp.dissociate(line['id'], sccp['id'])

        response = confd.lines(line['id']).endpoints.sccp.get()
        response.assert_status(404)



def test_get_line_associated_to_a_sccp_endpoint():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        response = confd.endpoints.sccp(sccp['id']).lines.get()
        response.assert_status(404)

        with a.line_endpoint_sccp(line, sccp):
            response = confd.endpoints.sccp(sccp['id']).lines.get()
            assert_that(
                response.item,
                has_entries(
                    line_id=line['id'],
                    endpoint_id=sccp['id'],
                    endpoint='sccp'
                )
            )



def test_associate():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        response = confd.lines(line['id']).endpoints.sccp(sccp['id']).put()
        response.assert_updated()



def test_associate_when_endpoint_already_associated():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        with a.line_endpoint_sccp(line, sccp):
            response = confd.lines(line['id']).endpoints.sccp(sccp['id']).put()
            response.assert_updated()


def test_associate_with_another_endpoint_when_already_associated():
    with fixtures.line() as line, fixtures.sccp() as sccp1, fixtures.sccp() as sccp2:
        with a.line_endpoint_sccp(line, sccp1):
            response = confd.lines(line['id']).endpoints.sccp(sccp2['id']).put()
            response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


def test_associate_multiple_lines_to_sccp():
    with fixtures.line() as line1, fixtures.line() as line2, fixtures.sccp() as sccp:
        with a.line_endpoint_sccp(line1, sccp):
            response = confd.lines(line2['id']).endpoints.sccp(sccp['id']).put()
            response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


def test_associate_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as _, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as __, fixtures.line(context='main-internal') as main_line, fixtures.line(context='sub-internal') as sub_line, fixtures.sccp(wazo_tenant=MAIN_TENANT) as main_sccp, fixtures.sccp(wazo_tenant=SUB_TENANT) as sub_sccp:
        response = confd.lines(main_line['id']).endpoints.sccp(sub_sccp['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

        response = confd.lines(sub_line['id']).endpoints.sccp(main_sccp['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('SCCPEndpoint'))

        response = confd.lines(main_line['id']).endpoints.sccp(sub_sccp['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        with a.line_endpoint_sccp(line, sccp, check=False):
            response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
            response.assert_deleted()


def test_dissociate_when_not_associated():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
        response.assert_deleted()



def test_dissociate_when_associated_to_user():
    with fixtures.line() as line, fixtures.sccp() as sccp, fixtures.user() as user:
        with a.line_endpoint_sccp(line, sccp), a.user_line(user, line):
            response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
            response.assert_match(400, e.resource_associated('Line', 'User'))


def test_dissociate_when_associated_to_extension():
    with fixtures.line() as line, fixtures.sccp() as sccp, fixtures.extension() as extension:
        with a.line_endpoint_sccp(line, sccp), a.line_extension(line, extension):
            response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
            response.assert_match(400, e.resource_associated('Line', 'Extension'))


def test_dissociate_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as _, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as __, fixtures.line(context='main-internal') as main_line, fixtures.line(context='sub-internal') as sub_line, fixtures.sccp(wazo_tenant=MAIN_TENANT) as main_sccp, fixtures.sccp(wazo_tenant=SUB_TENANT) as sub_sccp:
        response = confd.lines(main_line['id']).endpoints.sccp(sub_sccp['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

        response = confd.lines(sub_line['id']).endpoints.sccp(main_sccp['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('SCCPEndpoint'))



def test_get_endpoint_sccp_relation():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        with a.line_endpoint_sccp(line, sccp):
            response = confd.lines(line['id']).get()
            assert_that(
                response.item,
                has_entries(endpoint_sccp=has_entries(id=sccp['id']))
            )


def test_get_line_relation():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        with a.line_endpoint_sccp(line, sccp):
            response = confd.endpoints.sccp(sccp['id']).get()
            assert_that(
                response.item,
                has_entries(line=has_entries(id=line['id']))
            )


def test_delete_endpoint_dissociates_line():
    with fixtures.line() as line, fixtures.sccp() as sccp:
        with a.line_endpoint_sccp(line, sccp, check=False):
            response = confd.endpoints.sccp(sccp['id']).delete()
            response.assert_deleted()

            response = confd.lines(line['id']).endpoints.sccp.get()
            response.assert_status(404)
