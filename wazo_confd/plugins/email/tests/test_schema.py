# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from hamcrest import (
    assert_that,
    calling,
    contains_exactly,
    empty,
    has_entries,
    has_key,
    has_property,
)
from marshmallow import ValidationError
from unittest.mock import Mock
from wazo_test_helpers.hamcrest.raises import raises

from ..schema import EmailConfigSchema


class TestEmailConfigSchema(unittest.TestCase):
    def setUp(self):
        self.schema = EmailConfigSchema(handle_error=False)

    def test_address_rewriting_from_db_no_value(self):
        mail_config = Mock(
            mydomain='test.com',
            origin='a.test.com',
            relayhost='smtp.test.com',
            fallback_relayhost='smtp2.test.com',
            canonical='',
        )

        result = self.schema.dump(mail_config)
        assert_that(
            result,
            has_entries(
                domain_name='test.com',
                **{'from': 'a.test.com'},
                address_rewriting_rules=empty(),
                smtp_host='smtp.test.com',
                fallback_smtp_host='smtp2.test.com',
            ),
        )

    def test_address_rewriting_from_db_one_value(self):
        mail_config = Mock(
            mydomain='test.com',
            origin='a.test.com',
            relayhost='smtp.test.com',
            fallback_relayhost='smtp2.test.com',
            canonical='test1 test1@test.com',
        )

        result = self.schema.dump(mail_config)
        assert_that(
            result,
            has_entries(
                domain_name='test.com',
                **{'from': 'a.test.com'},
                address_rewriting_rules=contains_exactly(
                    has_entries(match='test1', replacement='test1@test.com'),
                ),
                smtp_host='smtp.test.com',
                fallback_smtp_host='smtp2.test.com',
            ),
        )

    def test_address_rewriting_from_db_multiple_values(self):
        mail_config = Mock(
            mydomain='test.com',
            origin='a.test.com',
            relayhost='smtp.test.com',
            fallback_relayhost='smtp2.test.com',
            canonical='test1 test1@test.com\\ntest2 test2@test.com',
        )

        result = self.schema.dump(mail_config)
        assert_that(
            result,
            has_entries(
                domain_name='test.com',
                **{'from': 'a.test.com'},
                address_rewriting_rules=contains_exactly(
                    has_entries(match='test1', replacement='test1@test.com'),
                    has_entries(match='test2', replacement='test2@test.com'),
                ),
                smtp_host='smtp.test.com',
                fallback_smtp_host='smtp2.test.com',
            ),
        )

    def test_address_rewriting_from_db_malformed_values(self):
        mail_config = Mock(
            mydomain='test.com',
            origin='a.test.com',
            relayhost='smtp.test.com',
            fallback_relayhost='smtp2.test.com',
            canonical='test1   test1@test.com\\ntest2  test2@test.com\\n',
        )

        result = self.schema.dump(mail_config)
        assert_that(
            result,
            has_entries(
                domain_name='test.com',
                **{'from': 'a.test.com'},
                address_rewriting_rules=contains_exactly(
                    has_entries(match='test1', replacement='test1@test.com'),
                    has_entries(match='test2', replacement='test2@test.com'),
                ),
                smtp_host='smtp.test.com',
                fallback_smtp_host='smtp2.test.com',
            ),
        )

    def test_address_rewriting_to_db(self):
        mail_config = {
            'domain_name': 'test.com',
            'from': 'a.test.com',
            'address_rewriting_rules': [
                {'match': 'test1', 'replacement': 'test1@test.com'},
                {'match': 'test2', 'replacement': 'test2@test.com'},
            ],
            'smtp_host': 'smtp.test.com',
            'fallback_smtp_host': 'smtp2.test.com',
        }

        result = self.schema.load(mail_config)
        assert_that(
            result,
            has_entries(
                mydomain='test.com',
                origin='a.test.com',
                relayhost='smtp.test.com',
                fallback_relayhost='smtp2.test.com',
                canonical='test1 test1@test.com\\ntest2 test2@test.com',
            ),
        )

    def test_address_rewriting_to_db_invalid_values(self):
        mail_config = {
            'domain_name': 'test.com',
            'from': 'a.test.com',
            'address_rewriting_rules': [
                {'match': 'test1', 'replacement': 'test1@test.com'},
                {'match': 'test2'},
            ],
            'smtp_host': 'smtp.test.com',
            'fallback_smtp_host': 'smtp2.test.com',
        }

        assert_that(
            calling(self.schema.load).with_args(mail_config),
            raises(
                ValidationError,
                has_property('messages', has_key('address_rewriting_rules')),
            ),
        )
