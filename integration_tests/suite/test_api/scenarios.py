# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

import re
import random
import string

from contextlib import contextmanager
from hamcrest import assert_that, contains, equal_to, has_length, has_entries
from xivo_test_helpers import until

from .bus import BusClient

import errors as e


class RelationScenario(object):

    FAKE_ID = 999999999

    left_resource = None
    right_resource = None

    @contextmanager
    def generated_resources(self):
        left_id, right_id = self.create_resources()
        yield left_id, right_id
        self.delete_resources(left_id, right_id)


class AssociationScenarios(RelationScenario):

    def test_association_when_left_does_not_exist(self):
        with self.generated_resources() as (left_id, right_id):
            error = e.not_found(resource=self.left_resource)
            response = self.associate_resources(self.FAKE_ID, right_id)
            response.assert_match(404, error)

    def test_association_when_right_does_not_exist(self):
        with self.generated_resources() as (left_id, right_id):
            error = e.not_found(resource=self.right_resource)
            response = self.associate_resources(left_id, self.FAKE_ID)
            response.assert_match(400, error)

    def test_association_when_resources_already_associated(self):
        with self.generated_resources() as (left_id, right_id):
            response = self.associate_resources(left_id, right_id)
            response.assert_status(201)

            error = e.resource_associated(left=self.left_resource, right=self.right_resource)
            response = self.associate_resources(left_id, right_id)
            response.assert_match(400, error)


class AssociationGetScenarios(RelationScenario):

    def test_get_association_when_left_does_not_exist(self):
        with self.generated_resources() as (left_id, right_id):
            error = e.not_found(resource=self.left_resource)
            response = self.get_association(self.FAKE_ID, right_id)
            response.assert_match(404, error)

    def test_get_association_when_right_does_not_exist(self):
        with self.generated_resources() as (left_id, right_id):
            error = e.not_found(resource=self.left_resource + self.right_resource)
            response = self.get_association(left_id, self.FAKE_ID)
            response.assert_match(404, error)


class AssociationGetCollectionScenarios(AssociationGetScenarios):

    def test_get_association_when_right_does_not_exist(self):
        with self.generated_resources() as (left_id, right_id):
            response = self.get_association(left_id, self.FAKE_ID)
            assert_that(response.items, contains())
            assert_that(response.json['total'], equal_to(0))


class DissociationScenarios(RelationScenario):

    def test_dissociation_when_left_does_not_exist(self):
        with self.generated_resources() as (left_id, right_id):
            error = e.not_found(resource=self.left_resource)
            response = self.dissociate_resources(self.FAKE_ID, right_id)
            response.assert_match(404, error)

    def test_dissociation_when_not_associated(self):
        with self.generated_resources() as (left_id, right_id):
            error = e.not_found(resource=self.left_resource + self.right_resource)
            response = self.dissociate_resources(left_id, right_id)
            response.assert_match(404, error)


class DissociationCollectionScenarios(DissociationScenarios):

    def test_dissociation_when_not_associated(self):
        with self.generated_resources() as (left_id, right_id):
            error = e.not_found(resource=self.right_resource)
            response = self.dissociate_resources(left_id, self.FAKE_ID)
            response.assert_match(404, error)


def check_resource_not_found(request, resource):
    response = request()
    response.assert_match(404, e.not_found(resource=resource))


def check_missing_required_field_returns_error(request, field):
    response = request({field: None})
    response.assert_match(400, re.compile(re.escape(field)))


def check_bogus_field_returns_error(request, field, bogus, required_field=None, message=None):
    message = message or field
    body = required_field if required_field else {}
    body[field] = bogus
    response = request(body)
    response.assert_match(400, re.compile(re.escape(message)))


def check_bogus_field_returns_error_matching_regex(request, field, bogus, regex):
    response = request({field: bogus})
    response.assert_match(400, re.compile(regex))


def random_string(length):
    return ''.join(random.choice(string.lowercase) for _ in range(length))


def random_digits(length):
    return ''.join(random.choice(string.digits) for _ in range(length))


def check_bus_event(routing_key, url, body=None):
    BusClient.listen_events(routing_key)
    url(body) if body else url()

    def assert_function():
        assert_that(BusClient.events(), has_length(1))

    until.assert_(assert_function, tries=5)


def search_error_checks(url):
    yield check_bogus_query_string_returns_error, url, 'order', 'invalid_column'
    yield check_bogus_query_string_returns_error, url, 'direction', 'invalid'
    yield check_bogus_query_string_returns_error, url, 'limit', -42
    yield check_bogus_query_string_returns_error, url, 'limit', 'invalid'
    yield check_bogus_query_string_returns_error, url, 'skip', -42
    yield check_bogus_query_string_returns_error, url, 'skip', 'invalid'
    yield check_bogus_query_string_returns_error, url, 'offset', -42
    yield check_bogus_query_string_returns_error, url, 'offset', 'invalid'


def check_bogus_query_string_returns_error(request, query_string, bogus):
    response = request(**{query_string: bogus})
    response.assert_match(400, re.compile(re.escape(query_string)))


def check_sorting(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(**{id_field: resource1[id_field]}),
                                         has_entries(**{id_field: resource2[id_field]})))

    response = url(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(**{id_field: resource2[id_field]}),
                                         has_entries(**{id_field: resource1[id_field]})))


def check_offset(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, offset=1)
    assert_that(response.items, contains(has_entries(**{id_field: resource2[id_field]})))


def check_offset_legacy(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, skip=1)
    assert_that(response.items, contains(has_entries(**{id_field: resource2[id_field]})))


def check_limit(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, limit=1)
    assert_that(response.items, contains(has_entries(**{id_field: resource1[id_field]})))
