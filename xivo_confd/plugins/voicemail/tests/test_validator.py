# -*- coding: utf-8 -*-

# Copyright 2013-2016 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest

from mock import Mock, sentinel
from hamcrest import assert_that, calling, raises

from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.helpers.exception import ResourceError

from xivo_confd.plugins.voicemail import validator


class TestNumberContextExists(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = validator.NumberContextExists(self.dao)

    def test_when_number_and_context_do_not_exist_then_validation_passes(self):
        model = Voicemail(number='1000',
                          context='context')
        self.dao.find_by.return_value = None

        self.validator.validate(model)

    def test_when_number_and_context_exist_then_validation_fails(self):
        model = Voicemail(number='1000',
                          context='context')
        self.dao.find_by.return_value = model

        assert_that(
            calling(self.validator.validate).with_args(model),
            raises(ResourceError))


class TestNumberContextChanged(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = validator.NumberContextChanged(self.dao)

    def test_when_number_and_context_do_not_exist_then_validation_passes(self):
        model = Voicemail(number='1000',
                          context='context')
        self.dao.find_by.return_value = None

        self.validator.validate(model)

    def test_when_number_and_context_have_not_changed_then_validation_passes(self):
        model = Voicemail(id=1,
                          number='1000',
                          context='context')
        self.dao.find_by.return_value = model

        self.validator.validate(model)

    def test_when_number_and_context_have_changed_and_new_number_context_do_not_exist_then_validation_passes(self):
        model = Voicemail(id=1,
                          number='1000',
                          context='context')
        self.dao.find_by.return_value = model
        model.number = '1001'
        model.context = 'default'

        self.validator.validate(model)

    def test_when_number_and_context_have_changed_and_new_number_context_exist_then_validation_fails(self):
        old_model = Voicemail(id=1,
                              number='1000',
                              context='context')
        new_model = Voicemail(id=2,
                              number='1001',
                              context='context')
        self.dao.find_by.return_value = old_model

        assert_that(
            calling(self.validator.validate).with_args(new_model),
            raises(ResourceError))


class TestAssociatedToUser(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = validator.AssociatedToUser()

    def test_when_no_associations_found_then_validation_passes(self):
        voicemail = Mock(Voicemail, id=sentinel.id, users=[])

        self.validator.validate(voicemail)

    def test_when_associations_found_then_validation_fails(self):
        voicemail = Mock(Voicemail, id=sentinel.id, users=[Mock(id=sentinel.user_id)])

        assert_that(
            calling(self.validator.validate).with_args(voicemail),
            raises(ResourceError))
