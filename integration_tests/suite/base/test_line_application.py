# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
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
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_ID = 999999999
FAKE_UUID = '00000000-0000-0000-0000-000000000000'


def test_associate_errors():
    with fixtures.line() as line, fixtures.application() as application:
        fake_line = confd.lines(FAKE_ID).applications(application['uuid']).put
        fake_application = confd.lines(line['id']).applications(FAKE_UUID).put

        s.check_resource_not_found(fake_line, 'Line')
        s.check_resource_not_found(fake_application, 'Application')



def test_dissociate_errors():
    with fixtures.line() as line, fixtures.application() as application:
        fake_line = confd.lines(FAKE_ID).applications(application['uuid']).delete
        fake_application = confd.lines(line['id']).applications(FAKE_UUID).delete

        s.check_resource_not_found(fake_line, 'Line')
        s.check_resource_not_found(fake_application, 'Application')



def test_associate():
    with fixtures.line() as line, fixtures.application() as application:
        response = confd.lines(line['id']).applications(application['uuid']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.line() as line, fixtures.application() as application:
        with a.line_application(line, application):
            response = confd.lines(line['id']).applications(application['uuid']).put()
            response.assert_updated()


def test_associate_multiple_applications_to_line():
    with fixtures.line() as line, fixtures.application() as application1, fixtures.application() as application2:
        with a.line_application(line, application1):
            response = confd.lines(line['id']).applications(application2['uuid']).put()
            response.assert_match(400, e.resource_associated('Line', 'Application'))


def test_associate_multiple_lines_to_application():
    with fixtures.line() as line1, fixtures.line() as line2, fixtures.application() as application:
        with a.line_application(line1, application):
            response = confd.lines(line2['id']).applications(application['uuid']).put()
            response.assert_updated()


def test_associate_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as _, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as __, fixtures.line(context='main-internal') as main_line, fixtures.line(context='sub-internal') as sub_line, fixtures.application(wazo_tenant=MAIN_TENANT) as main_app, fixtures.application(wazo_tenant=SUB_TENANT) as sub_app:
        response = confd.lines(main_line['id']).applications(sub_app['uuid']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

        response = confd.lines(sub_line['id']).applications(main_app['uuid']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Application'))

        response = confd.lines(main_line['id']).applications(sub_app['uuid']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.line() as line, fixtures.application() as application:
        with a.line_application(line, application, check=False):
            response = confd.lines(line['id']).applications(application['uuid']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.line() as line, fixtures.application() as application:
        response = confd.lines(line['id']).applications(application['uuid']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as _, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as __, fixtures.line(context='main-internal') as main_line, fixtures.line(context='sub-internal') as sub_line, fixtures.application(wazo_tenant=MAIN_TENANT) as main_app, fixtures.application(wazo_tenant=SUB_TENANT) as sub_app:
        response = confd.lines(main_line['id']).applications(sub_app['uuid']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

        response = confd.lines(sub_line['id']).applications(main_app['uuid']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Application'))



def test_get_line_relation():
    with fixtures.line() as line, fixtures.application() as application:
        with a.line_application(line, application):
            response = confd.lines(line['id']).get()
            assert_that(response.item, has_entries(
                application=has_entries(
                    uuid=application['uuid'],
                    name=application['name'],
                )
            ))


def test_get_application_relation():
    with fixtures.application() as application, fixtures.line() as line:
        with a.line_application(line, application):
            response = confd.applications(application['uuid']).get()
            assert_that(response.item, has_entries(
                lines=contains(
                    has_entries(
                        id=line['id'],
                        name=line['name'],
                    )
                )
            ))


def test_delete_line_when_line_and_application_associated():
    with fixtures.line() as line, fixtures.application() as application:
        with a.line_application(line, application, check=False):
            response = confd.lines(line['id']).delete()
            response.assert_deleted()


def test_delete_application_when_line_and_application_associated():
    with fixtures.line() as line, fixtures.application() as application:
        with a.line_application(line, application, check=False):
            response = confd.applications(application['uuid']).delete()
            response.assert_deleted()


def test_bus_events():
    with fixtures.line() as line, fixtures.application() as application:
        url = confd.lines(line['id']).applications(application['uuid'])
        routing_key = 'config.lines.{}.applications.{}.updated'.format(line['id'], application['uuid'])
        s.check_bus_event(routing_key, url.put)
        routing_key = 'config.lines.{}.applications.{}.deleted'.format(line['id'], application['uuid'])
        s.check_bus_event(routing_key, url.delete)

