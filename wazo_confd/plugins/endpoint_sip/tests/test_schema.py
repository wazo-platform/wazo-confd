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
    not_,
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
        body = {'transport': {'uuid': str(transport_uuid), 'name': 'ignored'}}

        loaded = self.schema.load(body)
        assert_that(
            loaded, has_entries(transport={'uuid': transport_uuid}),
        )

        body = {'transport': {'name': 'no uuid?'}}
        assert_that(
            calling(self.schema.load).with_args(body), raises(BadRequest),
        )

    def test_parents(self):
        parent_uuid = uuid.uuid4()
        body = {'parents': [{'uuid': str(parent_uuid), 'label': 'ignored'}]}
        loaded = self.schema.load(body)
        assert_that(
            loaded, has_entries(parents=contains({'uuid': parent_uuid})),
        )

        body = {'parents': [{'name': 'no uuid'}]}
        assert_that(
            calling(self.schema.load).with_args(body), raises(BadRequest),
        )

    def test_context(self):
        context_id = 42
        body = {'context': {'id': context_id}}
        loaded = self.schema.load(body)
        assert_that(loaded, has_entries(context={'id': context_id}))

        body = {'context': {'name': 'no id'}}
        assert_that(calling(self.schema.load).with_args(body), raises(BadRequest))

    def test_name(self):
        loaded = self.schema.load({})
        assert_that(loaded, has_entries(name=None))

        loaded = self.schema.load({'name': None})
        assert_that(loaded, has_entries(name=None))

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
