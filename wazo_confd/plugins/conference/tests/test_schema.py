# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, calling, raises
from werkzeug.exceptions import BadRequest

from wazo_confd.plugins.extension import schema as ExtensionSchema  # noqa
from wazo_confd.plugins.incall import schema as IncallSchema  # noqa

from ..schema import ConferenceSchema


class TestConferenceSchema(unittest.TestCase):
    def test_that_remb_estimated_bitrate_is_defined_when_force_is_used(self):
        body = {
            'remb_behavior': 'force',
        }

        schema = ConferenceSchema()
        assert_that(calling(schema.load).with_args(body), raises(BadRequest))
