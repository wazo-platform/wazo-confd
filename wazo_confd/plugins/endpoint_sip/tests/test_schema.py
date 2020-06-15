# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid
from unittest import TestCase

from hamcrest import (
    assert_that,
    calling,
    contains,
    contains_inanyorder,
    has_entries,
    has_length,
)

from xivo_test_helpers.hamcrest.raises import raises
from werkzeug.exceptions import BadRequest


# Adding schemas to the marshmallow registry
from wazo_confd.plugins.trunk.resource import TrunkSchema  # noqa
from wazo_confd.plugins.line.resource import LineSchema  # noqa

from ..schema import EndpointSIPSchema, EndpointSIPSchemaNullable


class TestEndpointSIPSchema(TestCase):
    def setUp(self):
        self.schema = EndpointSIPSchema()

    def test_transport(self):
        transport_uuid = uuid.uuid4()
        body = self.new(transport={'uuid': str(transport_uuid), 'name': 'ignored'})

        loaded = self.schema.load(body)
        assert_that(
            loaded, has_entries(transport={'uuid': transport_uuid}),
        )

        body = self.new(transport={'name': 'no uuid?'})
        assert_that(
            calling(self.schema.load).with_args(body), raises(BadRequest),
        )

    def test_parents(self):
        parent_uuid = uuid.uuid4()
        body = self.new(parents=[{'uuid': str(parent_uuid), 'label': 'ignored'}],)
        loaded = self.schema.load(body)
        assert_that(
            loaded, has_entries(parents=contains({'uuid': parent_uuid})),
        )

        body = self.new(parents=[{'name': 'no uuid?'}])
        assert_that(
            calling(self.schema.load).with_args(body), raises(BadRequest),
        )

    def test_context(self):
        context_id = 42
        body = self.new(context={'id': context_id})
        loaded = self.schema.load(body)
        assert_that(loaded, has_entries(context={'id': context_id}))

        body = self.new(context={'name': 'no id'})
        assert_that(calling(self.schema.load).with_args(body), raises(BadRequest))

    def test_name(self):
        loaded = self.schema.load({})
        assert_that(loaded, has_entries(name=None))

        loaded = self.schema.load({'name': None})
        assert_that(loaded, has_entries(name=None))

        assert_that(
            calling(self.schema.load).with_args({'name': ''}), raises(BadRequest),
        )

    # TODO(pc-m): remove this function if it's not useful
    def new(self, **kwargs):
        return kwargs


class TestEndpointSIPSchemaNullable(TestCase):

    schema = EndpointSIPSchemaNullable()

    def test_that_sip_username_and_sip_secret_are_read(self):
        body = {'username': 'my-username', 'secret': 'my-password'}

        loaded = self.schema.load(body)

        assert_that(
            loaded,
            has_entries(
                auth_section_options=contains_inanyorder(
                    contains('username', 'my-username'),
                    contains('password', 'my-password'),
                )
            ),
        )

    def test_that_a_username_and_a_password_are_generated(self):
        body = {}

        loaded = self.schema.load(body)

        assert_that(
            loaded,
            has_entries(
                auth_section_options=contains_inanyorder(
                    contains('username', has_length(8)),
                    contains('password', has_length(8)),
                )
            ),
        )
