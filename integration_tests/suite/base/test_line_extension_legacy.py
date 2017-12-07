# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import scenarios as s
from ..helpers import fixtures as f
from ..helpers.helpers.extension import generate_extension, delete_extension
from ..helpers.helpers.line_sip import generate_line, delete_line

from . import confd


class TestLineExtensionAssociation(s.AssociationScenarios, s.DissociationScenarios, s.AssociationGetScenarios):

    left_resource = "Line"
    right_resource = "Extension"

    def create_resources(self):
        line = generate_line()
        extension = generate_extension()
        return line['id'], extension['id']

    def delete_resources(self, line_id, extension_id):
        delete_line(line_id)
        delete_extension(extension_id)

    def associate_resources(self, line_id, extension_id):
        return confd.lines(line_id).extension.post(extension_id=extension_id)

    def dissociate_resources(self, line_id, extension_id):
        return confd.lines(line_id).extension.delete()

    def get_association(self, line_id, extension_id):
        return confd.lines(line_id).extension.get()


@f.line_sip()
@f.extension()
def test_associate_line_and_extension(line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    response = confd.lines(line['id']).extension.post(extension_id=extension['id'])
    response.assert_created('lines', 'extension')
    assert_that(response.item, expected)


@f.user()
@f.line_sip()
@f.extension()
def test_associate_user_line_extension(user, line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    with a.user_line(user, line, check=False):
        response = confd.lines(line['id']).extension.post(extension_id=extension['id'])
        response.assert_created('lines', 'extension')
        assert_that(response.item, expected)


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
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    with a.line_extension(line, extension):
        response = confd.lines(line['id']).extension.get()
        assert_that(response.item, expected)


@f.line_sip()
@f.extension()
def test_get_extension_from_line(line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    with a.line_extension(line, extension):
        response = confd.extensions(extension['id']).line.get()
        assert_that(response.item, expected)


@f.user()
@f.line_sip()
@f.extension()
@f.device()
def test_dissociate_when_line_associated_to_device(user, line, extension, device):
    with a.line_extension(line, extension), a.user_line(user, line), a.line_device(line, device):
        response = confd.lines(line['id']).extension.delete()
        response.assert_match(400, e.resource_associated('Line', 'Device'))
