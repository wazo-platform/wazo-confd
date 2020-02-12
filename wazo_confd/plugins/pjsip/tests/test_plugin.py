# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
import unittest
import gzip
import json

from hamcrest import assert_that, calling, equal_to, has_properties
from xivo_test_helpers.hamcrest.raises import raises

from ..plugin import PJSIPDoc
from ..exceptions import PJSIPDocError

VALID_BODY = {
    'endpoint': {
        '100rel': {
            'name': '100rel',
            'default': 'yes',
            'synopsis': 'Allow support for RFC3262 provisional ACK tags',
            'description': '',
            'note': '',
            'choices': {'no': '', 'required': '', 'yes': ''},
        }
    }
}


class TestPJSIPDoc(unittest.TestCase):
    def test_get_valid_file(self):
        with tempfile.NamedTemporaryFile('w+b', suffix='.gz') as f:
            f.write(gzip.compress(json.dumps(VALID_BODY).encode()))
            f.flush()

            doc = PJSIPDoc(f.name)

            result = doc.get()

            assert_that(result, equal_to(VALID_BODY))

    def test_get_no_file(self):
        with tempfile.NamedTemporaryFile('w+b', suffix='.gz') as f:
            filename = f.name

        doc = PJSIPDoc(filename)

        assert_that(
            calling(doc.get),
            raises(PJSIPDocError).matching(
                has_properties(
                    status_code=400, message='failed to read PJSIP JSON documentation',
                )
            ),
        )

    def test_get_invalid_json(self):
        with tempfile.NamedTemporaryFile('w+b', suffix='.gz') as f:
            f.write(gzip.compress(b'this is not json'))
            f.flush()

            doc = PJSIPDoc(f.name)

            assert_that(
                calling(doc.get),
                raises(PJSIPDocError).matching(
                    has_properties(
                        status_code=400,
                        message='failed to read PJSIP JSON documentation',
                    )
                ),
            )

    def test_get_not_a_gzip(self):
        with tempfile.NamedTemporaryFile('w+b', suffix='.gz') as f:
            f.write(json.dumps(VALID_BODY).encode())
            f.flush()

            doc = PJSIPDoc(f.name)

            assert_that(
                calling(doc.get),
                raises(PJSIPDocError).matching(
                    has_properties(
                        status_code=400,
                        message='failed to read PJSIP JSON documentation',
                    )
                ),
            )
