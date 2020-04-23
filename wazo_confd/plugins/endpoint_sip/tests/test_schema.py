# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid
from unittest import TestCase

from hamcrest import assert_that, calling, contains, has_entries

from xivo_test_helpers.hamcrest.raises import raises
from werkzeug.exceptions import BadRequest


# Adding schemas to the marshmallow registry
from wazo_confd.plugins.trunk.resource import TrunkSchema  # noqa
from wazo_confd.plugins.line.resource import LineSchema  # noqa

from ..schema import EndpointSIPSchema


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
        body = self.new(
            parents=[{'uuid': str(parent_uuid), 'display_name': 'ignored'}],
        )
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

    # TODO(pc-m): remove this function if it's not useful
    def new(self, **kwargs):
        return kwargs
