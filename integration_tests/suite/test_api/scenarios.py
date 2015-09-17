from contextlib import contextmanager

from hamcrest import assert_that, contains, equal_to

from test_api import client
import errors as e


class Scenarios(object):

    url = None
    resource = None
    required = []
    bogus_fields = []

    @contextmanager
    def generated_url(self):
        resource_id = self.create_resource()
        yield self.generate_url(resource_id)
        self.delete_resource(resource_id)

    def generate_url(self, resource_id):
        return "{}/{}".format(self.url, resource_id)

    def delete_resource(self, resource_id):
        url = self.generate_url(resource_id)
        client.delete(url)

    def post_resource(self, parameters):
        response = client.post(self.url, parameters)
        return response


class GetScenarios(Scenarios):

    def test_resource_does_not_exist_on_get(self):
        resource_id = self.create_resource()
        self.delete_resource(resource_id)

        url = self.generate_url(resource_id)

        error = e.not_found(resource=self.resource)
        response = client.get(url)

        response.assert_match(404, error)


class CreateScenarios(Scenarios):

    def test_missing_parameters_on_post(self):
        for field in self.required:
            yield self.check_missing_field_on_post, field

    def check_missing_field_on_post(self, field):
        error = e.missing_parameters(field)
        response = client.post(self.url, {})
        response.assert_match(400, error)

    def test_unknown_parameter_on_post(self):
        error = e.unknown_parameters('invalid')
        response = self.post_resource({'invalid': 'invalid'})

        response.assert_match(400, error)

    def test_wrong_parameter_type_on_post(self):
        for bogus_field in self.bogus_fields:
            yield self.check_bogus_field_on_post, bogus_field

    def check_bogus_field_on_post(self, bogus_field):
        field, value, expected_type = bogus_field

        error = e.wrong_type(field=field, type=expected_type)
        response = self.post_resource({field: value})

        response.assert_match(400, error)


class EditScenarios(Scenarios):

    def test_unknown_parameter_on_put(self):
        with self.generated_url() as url:
            error = e.unknown_parameters('invalid')
            response = client.put(url, {'invalid': 'invalidvalue'})
            response.assert_match(400, error)

    def test_wrong_parameter_type_on_put(self):
        with self.generated_url() as url:
            for bogus_field in self.bogus_fields:
                yield self.check_bogus_field_on_put, url, bogus_field

    def test_resource_not_found_on_put(self):
        resource_id = self.create_resource()
        self.delete_resource(resource_id)

        error = e.not_found(resource=self.resource)
        response = client.put(self.generate_url(resource_id), {'param': 'param'})

        response.assert_match(404, error)

    def check_bogus_field_on_put(self, url, bogus_field):
        field, value, expected_type = bogus_field
        error = e.wrong_type(field=field, type=expected_type)

        response = client.put(url, {field: value})
        response.assert_match(400, error)


class DeleteScenarios(Scenarios):

    def test_resource_not_found_on_delete(self):
        resource_id = self.create_resource()
        self.delete_resource(resource_id)

        url = self.generate_url(resource_id)

        error = e.not_found(resource=self.resource)
        response = client.delete(url)

        response.assert_match(404, error)


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
