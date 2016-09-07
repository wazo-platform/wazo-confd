import re

from contextlib import contextmanager

from hamcrest import assert_that, contains, equal_to

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
