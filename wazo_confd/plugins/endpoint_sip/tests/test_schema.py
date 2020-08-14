# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid
from unittest import TestCase

from hamcrest import (
    assert_that,
    calling,
    contains,
    empty,
    has_entries,
    not_,
)

from xivo_test_helpers.hamcrest.raises import raises
from werkzeug.exceptions import BadRequest


# Adding schemas to the marshmallow registry
from wazo_confd.plugins.trunk.resource import TrunkSchema  # noqa
from wazo_confd.plugins.line.resource import LineSchema  # noqa

from ..schema import EndpointSIPSchema, EndpointSIPEventSchema


class TestEndpointSIPSchema(TestCase):
    def setUp(self):
        self.schema = EndpointSIPSchema()

    def test_transport(self):
        transport_uuid = uuid.uuid4()
        body = {'transport': {'uuid': str(transport_uuid), 'name': 'ignored'}}

        loaded = self.schema.load(body)
        assert_that(
            loaded, has_entries(transport={'uuid': transport_uuid}),
        )

        body = {'transport': {'name': 'no uuid?'}}
        assert_that(
            calling(self.schema.load).with_args(body), raises(BadRequest),
        )

    def test_templates(self):
        template_uuid = uuid.uuid4()
        body = {'templates': [{'uuid': str(template_uuid), 'label': 'ignored'}]}
        loaded = self.schema.load(body)
        assert_that(
            loaded, has_entries(templates=contains({'uuid': template_uuid})),
        )

        body = {'templates': [{'name': 'no uuid'}]}
        assert_that(
            calling(self.schema.load).with_args(body), raises(BadRequest),
        )

    def test_name(self):
        loaded = self.schema.load({})
        assert_that(loaded, not_(has_entries(name=None)))

        assert_that(
            calling(self.schema.load).with_args({'name': None}), raises(BadRequest),
        )

        assert_that(
            calling(self.schema.load).with_args({'name': ''}), raises(BadRequest),
        )

    def test_option_length(self):
        body = {
            'aor_section_options': [
                ['key_{}'.format(i), '{}'.format(i)] for i in range(513)
            ],
        }
        assert_that(calling(self.schema.load).with_args(body), raises(BadRequest))

        body = {
            'aor_section_options': [
                ['key_{}'.format(i), '{}'.format(i)] for i in range(512)
            ],
        }
        assert_that(calling(self.schema.load).with_args(body), not_(raises(BadRequest)))


class TestEndpointSIPEventSchema(TestCase):
    def setUp(self):
        self.schema = EndpointSIPEventSchema()

    def test_auth_section_options_is_removed_except_username(self):
        body = {
            'auth_section_options': [['username', 'username'], ['password', 'password']]
        }
        loaded = self.schema.dump(body)
        assert_that(
            loaded,
            has_entries(auth_section_options=contains(['username', 'username'])),
        )

        body = {'auth_section_options': [['password', 'password']]}
        loaded = self.schema.dump(body)
        assert_that(loaded, has_entries(auth_section_options=empty()))
