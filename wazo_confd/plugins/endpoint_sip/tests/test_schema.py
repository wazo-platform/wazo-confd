# Copyright 2019-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid
from unittest import TestCase

from hamcrest import (
    assert_that,
    calling,
    contains_exactly,
    empty,
    equal_to,
    has_entries,
    not_,
)

from wazo_test_helpers.hamcrest.raises import raises
from werkzeug.exceptions import BadRequest


# Adding schemas to the marshmallow registry
from wazo_confd.plugins.trunk.resource import TrunkSchema  # noqa
from wazo_confd.plugins.line.resource import LineListSchema  # noqa

from ..schema import (
    EndpointSIPSchema,
    GETQueryStringSchema,
    MergedEndpointSIPSchema,
)


class TestGETQueryStringSchema(TestCase):
    def setUp(self):
        self.schema = GETQueryStringSchema()

    def test_view_valid(self):
        query_string = {'view': 'merged'}

        loaded = self.schema.load(query_string)

        assert_that(loaded, equal_to({'view': 'merged'}))

    def test_view_invalid(self):
        query_string = {'view': 'not-merged'}

        assert_that(
            calling(self.schema.load).with_args(query_string), raises(Exception)
        )

    def test_view_not_specified(self):
        query_string = {}

        loaded = self.schema.load(query_string)

        assert_that(loaded, equal_to({'view': None}))


class TestEndpointSIPSchema(TestCase):
    def setUp(self):
        self.schema = EndpointSIPSchema()

    def test_transport(self):
        transport_uuid = uuid.uuid4()
        body = {'transport': {'uuid': str(transport_uuid), 'name': 'ignored'}}

        loaded = self.schema.load(body)
        assert_that(
            loaded,
            has_entries(transport={'uuid': transport_uuid}),
        )

        body = {'transport': {'name': 'no uuid?'}}
        assert_that(
            calling(self.schema.load).with_args(body),
            raises(BadRequest),
        )

    def test_templates(self):
        template_uuid = uuid.uuid4()
        body = {'templates': [{'uuid': str(template_uuid), 'label': 'ignored'}]}
        loaded = self.schema.load(body)
        assert_that(
            loaded,
            has_entries(templates=contains_exactly({'uuid': template_uuid})),
        )

        body = {'templates': [{'name': 'no uuid'}]}
        assert_that(
            calling(self.schema.load).with_args(body),
            raises(BadRequest),
        )

    def test_name(self):
        loaded = self.schema.load({})
        assert_that(loaded, not_(has_entries(name=None)))

        assert_that(
            calling(self.schema.load).with_args({'name': None}),
            raises(BadRequest),
        )

        assert_that(
            calling(self.schema.load).with_args({'name': ''}),
            raises(BadRequest),
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

    def test_get_attribute_with_only_on_section_options(self):
        self.schema = EndpointSIPSchema(only=['auth_section_options.username'])
        body = {
            'auth_section_options': [['username', 'username'], ['password', 'password']]
        }
        loaded = self.schema.dump(body)
        assert_that(
            loaded,
            has_entries(
                auth_section_options=contains_exactly(['username', 'username'])
            ),
        )

        body = {'auth_section_options': [['password', 'password']]}
        loaded = self.schema.dump(body)
        assert_that(loaded, has_entries(auth_section_options=empty()))

        body = {
            'auth_section_options': [
                ['username', 'username1'],
                ['username', 'username2'],
                ['password', 'password'],
            ]
        }
        loaded = self.schema.dump(body)
        assert_that(
            loaded,
            has_entries(
                auth_section_options=contains_exactly(
                    ['username', 'username1'],
                    ['username', 'username2'],
                )
            ),
        )


class TestMergedEndpointSIPSchema(TestCase):
    def test_get_attribute_with_attribute(self):
        self.schema = MergedEndpointSIPSchema()
        body = {'combined_auth_section_options': [['username', 'username']]}
        loaded = self.schema.dump(body)
        assert_that(
            loaded,
            has_entries(
                auth_section_options=contains_exactly(('username', 'username'))
            ),
        )

    def test_get_attribute_with_attribute_and_only(self):
        self.schema = MergedEndpointSIPSchema(only=['auth_section_options.username'])
        body = {
            'combined_auth_section_options': [
                ['username', 'username'],
                ['password', 'password'],
            ]
        }
        loaded = self.schema.dump(body)
        assert_that(
            loaded,
            has_entries(
                auth_section_options=contains_exactly(('username', 'username'))
            ),
        )
