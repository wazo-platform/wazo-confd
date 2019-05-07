# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures as f,
    scenarios as s,
)

FAKE_ID = 999999999


@f.line()
@f.extension()
def test_associate_errors(line, extension):
    response = confd.lines(FAKE_ID).extension.post(extension_id=extension['id'])
    response.assert_match(404, e.not_found(resource='Line'))

    response = confd.lines(line['id']).extension.post(extension_id=FAKE_ID)
    response.assert_match(400, e.not_found(resource='Extension'))


@f.line()
@f.extension()
def test_dissociate_errors(line, extension):
    fake_line = confd.lines(FAKE_ID).extension.delete
    yield s.check_resource_not_found, fake_line, 'Line'


def test_get_errors():
    fake_line = confd.lines(FAKE_ID).extension.get
    yield s.check_resource_not_found, fake_line, 'Line'


@f.extension()
@f.line_sip()
def test_associate_line_to_extension_already_associated(extension, line):
    with a.line_extension(line, extension):
        response = confd.lines(line['id']).extension.post(extension_id=extension['id'])
        response.assert_ok()


@f.line_sip()
@f.extension()
def test_dissociate_not_associated(line, extension):
    response = confd.lines(line['id']).extension.delete()
    response.assert_match(404, e.not_found(resource='LineExtension'))


@f.line_sip()
@f.extension()
def test_associate_line_and_extension(line, extension):
    response = confd.lines(line['id']).extension.post(extension_id=extension['id'])
    response.assert_created('lines', 'extension')
    assert_that(
        response.item,
        has_entries(line_id=line['id'], extension_id=extension['id'])
    )


@f.user()
@f.line_sip()
@f.extension()
def test_associate_user_line_extension(user, line, extension):
    with a.user_line(user, line, check=False):
        response = confd.lines(line['id']).extension.post(extension_id=extension['id'])
        response.assert_created('lines', 'extension')
        assert_that(
            response.item,
            has_entries(line_id=line['id'], extension_id=extension['id'])
        )


@f.user()
@f.line_sip()
@f.extension()
def test_dissociate_user_line_extension(user, line, extension):
    with a.user_line(user, line), a.line_extension(line, extension, check=False):
        response = confd.lines(line['id']).extension.delete()
        response.assert_deleted()


@f.line_sip()
@f.extension()
def test_get_line_from_extension(line, extension):
    with a.line_extension(line, extension):
        response = confd.lines(line['id']).extension.get()
        assert_that(
            response.item,
            has_entries(line_id=line['id'], extension_id=extension['id'])
        )


@f.line_sip()
@f.extension()
def test_get_extension_from_line(line, extension):
    with a.line_extension(line, extension):
        response = confd.extensions(extension['id']).line.get()
        assert_that(
            response.item,
            has_entries(line_id=line['id'], extension_id=extension['id'])
        )


@f.user()
@f.line_sip()
@f.extension()
@f.device()
def test_dissociate_when_line_associated_to_device(user, line, extension, device):
    with a.line_extension(line, extension), a.user_line(user, line), a.line_device(line, device):
        response = confd.lines(line['id']).extension.delete()
        response.assert_match(400, e.resource_associated('Line', 'Device'))
