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
    with fixtures.line() as line, fixtures.sip() as sip:
        fake_line = confd.lines(999999999).endpoints.sip(sip['id']).put
        fake_sip = confd.lines(line['id']).endpoints.sip(999999999).put

        s.check_resource_not_found(fake_line, 'Line')
        s.check_resource_not_found(fake_sip, 'SIPEndpoint')



def test_dissociate_errors():
    with fixtures.line() as line, fixtures.sip() as sip:
        fake_line = confd.lines(999999999).endpoints.sip(sip['id']).delete
        fake_sip = confd.lines(line['id']).endpoints.sip(999999999).delete

        s.check_resource_not_found(fake_line, 'Line')
        s.check_resource_not_found(fake_sip, 'SIPEndpoint')



def test_get_errors():
    fake_line = confd.lines(999999999).endpoints.sip.get
    fake_sip = confd.endpoints.sip(999999999).lines.get

    s.check_resource_not_found(fake_line, 'Line')
    s.check_resource_not_found(fake_sip, 'SIPEndpoint')


def test_get_sip_endpoint_associated_to_line():
    with fixtures.line() as line, fixtures.sip() as sip:
        response = confd.lines(line['id']).endpoints.sip.get()
        response.assert_status(404)

        with a.line_endpoint_sip(line, sip):
            response = confd.lines(line['id']).endpoints.sip.get()
            assert_that(
                response.item,
                has_entries(
                    line_id=line['id'],
                    endpoint_id=sip['id'],
                    endpoint='sip',
                )
            )



def test_get_sip_endpoint_after_dissociation():
    with fixtures.line() as line, fixtures.sip() as sip:
        h.line_endpoint_sip.associate(line['id'], sip['id'])
        h.line_endpoint_sip.dissociate(line['id'], sip['id'])

        response = confd.lines(line['id']).endpoints.sip.get()
        response.assert_status(404)



def test_get_line_associated_to_a_sip_endpoint():
    with fixtures.line() as line, fixtures.sip() as sip:
        response = confd.endpoints.sip(sip['id']).lines.get()
        response.assert_status(404)

        with a.line_endpoint_sip(line, sip):
            response = confd.endpoints.sip(sip['id']).lines.get()
            assert_that(
                response.item,
                has_entries(
                    line_id=line['id'],
                    endpoint_id=sip['id'],
                    endpoint='sip',
                )
            )



def test_associate():
    with fixtures.line() as line, fixtures.sip() as sip:
        response = confd.lines(line['id']).endpoints.sip(sip['id']).put()
        response.assert_updated()



def test_associate_when_endpoint_already_associated():
    with fixtures.line() as line, fixtures.sip() as sip:
        with a.line_endpoint_sip(line, sip):
            response = confd.lines(line['id']).endpoints.sip(sip['id']).put()
            response.assert_updated()


def test_associate_with_another_endpoint_when_already_associated():
    with fixtures.line() as line, fixtures.sip() as sip1, fixtures.sip() as sip2:
        with a.line_endpoint_sip(line, sip1):
            response = confd.lines(line['id']).endpoints.sip(sip2['id']).put()
            response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


def test_associate_multiple_lines_to_sip():
    with fixtures.line() as line1, fixtures.line() as line2, fixtures.sip() as sip:
        with a.line_endpoint_sip(line1, sip):
            response = confd.lines(line2['id']).endpoints.sip(sip['id']).put()
            response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


def test_associate_when_trunk_already_associated():
    with fixtures.line() as line, fixtures.trunk() as trunk, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk, sip):
            response = confd.lines(line['id']).endpoints.sip(sip['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


def test_associate_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as _, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as __, fixtures.line(context='main-internal') as main_line, fixtures.line(context='sub-internal') as sub_line, fixtures.sip(wazo_tenant=MAIN_TENANT) as main_sip, fixtures.sip(wazo_tenant=SUB_TENANT) as sub_sip:
        response = confd.lines(main_line['id']).endpoints.sip(sub_sip['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

        response = confd.lines(sub_line['id']).endpoints.sip(main_sip['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('SIPEndpoint'))

        response = confd.lines(main_line['id']).endpoints.sip(sub_sip['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.line() as line, fixtures.sip() as sip:
        with a.line_endpoint_sip(line, sip, check=False):
            response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
            response.assert_deleted()


def test_dissociate_when_not_associated():
    with fixtures.line() as line, fixtures.sip() as sip:
        response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
        response.assert_deleted()



def test_dissociate_when_associated_to_user():
    with fixtures.line() as line, fixtures.sip() as sip, fixtures.user() as user:
        with a.line_endpoint_sip(line, sip), a.user_line(user, line):
            response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
            response.assert_match(400, e.resource_associated('Line', 'User'))


def test_dissociate_when_associated_to_extension():
    with fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension:
        with a.line_endpoint_sip(line, sip), a.line_extension(line, extension):
            response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
            response.assert_match(400, e.resource_associated('Line', 'Extension'))


def test_dissociate_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as _, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as __, fixtures.line(context='main-internal') as main_line, fixtures.line(context='sub-internal') as sub_line, fixtures.sip(wazo_tenant=MAIN_TENANT) as main_sip, fixtures.sip(wazo_tenant=SUB_TENANT) as sub_sip:
        response = confd.lines(main_line['id']).endpoints.sip(sub_sip['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

        response = confd.lines(sub_line['id']).endpoints.sip(main_sip['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('SIPEndpoint'))



def test_get_endpoint_sip_relation():
    with fixtures.line() as line, fixtures.sip() as sip:
        with a.line_endpoint_sip(line, sip):
            response = confd.lines(line['id']).get()
            assert_that(
                response.item,
                has_entries(endpoint_sip=has_entries(
                    id=sip['id'],
                    username=sip['username'],
                ))
            )


def test_get_line_relation():
    with fixtures.line() as line, fixtures.sip() as sip:
        with a.line_endpoint_sip(line, sip):
            response = confd.endpoints.sip(sip['id']).get()
            assert_that(
                response.item,
                has_entries(line=has_entries(id=line['id']))
            )


def test_delete_endpoint_dissociates_line():
    with fixtures.line() as line, fixtures.sip() as sip:
        with a.line_endpoint_sip(line, sip, check=False):
            response = confd.endpoints.sip(sip['id']).delete()
            response.assert_deleted()

            response = confd.lines(line['id']).endpoints.sip.get()
            response.assert_status(404)
