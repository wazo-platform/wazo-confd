# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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


@fixtures.line()
@fixtures.application()
def test_associate_errors(line, application):
    fake_line = confd.lines(FAKE_ID).applications(application['uuid']).put
    fake_application = confd.lines(line['id']).applications(FAKE_UUID).put

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_application, 'Application'


@fixtures.line()
@fixtures.application()
def test_dissociate_errors(line, application):
    fake_line = confd.lines(FAKE_ID).applications(application['uuid']).delete
    fake_application = confd.lines(line['id']).applications(FAKE_UUID).delete

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_application, 'Application'


@fixtures.line()
@fixtures.application()
def test_associate(line, application):
    response = confd.lines(line['id']).applications(application['uuid']).put()
    response.assert_updated()


@fixtures.line()
@fixtures.application()
def test_associate_already_associated(line, application):
    with a.line_application(line, application):
        response = confd.lines(line['id']).applications(application['uuid']).put()
        response.assert_updated()


@fixtures.line()
@fixtures.application()
@fixtures.application()
def test_associate_multiple_applications_to_line(line, application1, application2):
    with a.line_application(line, application1):
        response = confd.lines(line['id']).applications(application2['uuid']).put()
        response.assert_match(400, e.resource_associated('Line', 'Application'))


@fixtures.line()
@fixtures.line()
@fixtures.application()
def test_associate_multiple_lines_to_application(line1, line2, application):
    with a.line_application(line1, application):
        response = confd.lines(line2['id']).applications(application['uuid']).put()
        response.assert_updated()


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line(context='main-internal')
@fixtures.line(context='sub-internal')
@fixtures.application(wazo_tenant=MAIN_TENANT)
@fixtures.application(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(_, __, main_line, sub_line, main_app, sub_app):
    response = confd.lines(main_line['id']).applications(sub_app['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Line'))

    response = confd.lines(sub_line['id']).applications(main_app['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Application'))

    response = confd.lines(main_line['id']).applications(sub_app['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.line()
@fixtures.application()
def test_dissociate(line, application):
    with a.line_application(line, application, check=False):
        response = confd.lines(line['id']).applications(application['uuid']).delete()
        response.assert_deleted()


@fixtures.line()
@fixtures.application()
def test_dissociate_not_associated(line, application):
    response = confd.lines(line['id']).applications(application['uuid']).delete()
    response.assert_deleted()


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line(context='main-internal')
@fixtures.line(context='sub-internal')
@fixtures.application(wazo_tenant=MAIN_TENANT)
@fixtures.application(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(_, __, main_line, sub_line, main_app, sub_app):
    response = confd.lines(main_line['id']).applications(sub_app['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Line'))

    response = confd.lines(sub_line['id']).applications(main_app['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Application'))


@fixtures.line()
@fixtures.application()
def test_delete_line_when_line_and_application_associated(line, application):
    with a.line_application(line, application, check=False):
        response = confd.lines(line['id']).delete()
        response.assert_deleted()


@fixtures.line()
@fixtures.application()
def test_delete_application_when_line_and_application_associated(line, application):
    with a.line_application(line, application, check=False):
        response = confd.applications(application['uuid']).delete()
        response.assert_deleted()


@fixtures.line()
@fixtures.application()
def test_bus_events(line, application):
    url = confd.lines(line['id']).applications(application['uuid'])
    routing_key = 'config.lines.{}.applications.{}.updated'.format(line['id'], application['uuid'])
    yield s.check_bus_event, routing_key, url.put
    routing_key = 'config.lines.{}.applications.{}.deleted'.format(line['id'], application['uuid'])
    yield s.check_bus_event, routing_key, url.delete
