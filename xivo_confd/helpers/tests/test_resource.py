# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from mock import Mock, patch, sentinel
from hamcrest import assert_that, equal_to

from xivo_confd.helpers.resource import CRUDResource, CRUDService, AssociationResource


@patch('xivo_confd.helpers.resource.url_for')
@patch('xivo_confd.helpers.resource.request')
class TestCRUDResource(unittest.TestCase):

    def setUp(self):
        self.service = Mock()
        self.converter = Mock()
        self.extra_parameters = ['extra']
        self.resource = CRUDResource(self.service, self.converter, self.extra_parameters)

    @patch('xivo_confd.helpers.resource.extract_search_parameters')
    def test_when_search_requested_then_search_service_called(self, mock_extract, request, _):
        expected_parameters = mock_extract.return_value

        self.resource.search()

        mock_extract.assert_called_once_with(request.args, self.extra_parameters)
        self.service.search.assert_called_once_with(expected_parameters)

    def test_when_search_requested_then_search_result_converted(self, request, _):
        request.args = {}
        search_result = self.service.search.return_value
        expected_response = self.converter.encode_list.return_value

        response = self.resource.search()

        self.converter.encode_list.assert_that_called_once_with(search_result.items,
                                                                search_result.total)
        assert_that(response,
                    equal_to((expected_response,
                              200,
                              {'Content-Type': 'application/json'})))

    def test_when_get_requested_then_service_called(self, request, _):
        self.resource.get(sentinel.resource_id)

        self.service.get.assert_called_once_with(sentinel.resource_id)

    def test_when_get_requested_then_resource_encoded(self, request, url_for):
        expected_resource = self.service.get.return_value
        expected_response = self.converter.encode.return_value
        expected_location = url_for.return_value

        response = self.resource.get(sentinel.resource_id)

        self.converter.encode.assert_called_once_with(expected_resource)
        url_for.assert_called_once_with('.get', resource_id=expected_resource.id)
        assert_that(response,
                    equal_to((expected_response,
                              200,
                              {'Location': expected_location,
                               'Content-Type': 'application/json'})))

    def test_when_create_requested_then_request_decoded(self, request, _):
        self.resource.create()

        self.converter.decode.assert_called_once_with(request)

    def test_when_create_requested_then_service_called(self, request, _):
        expected_resource = self.converter.decode.return_value

        self.resource.create()

        self.service.create.assert_called_once_with(expected_resource)

    def test_when_create_requested_then_resource_encoded(self, request, url_for):
        expected_resource = self.service.create.return_value
        expected_response = self.converter.encode.return_value
        expected_location = url_for.return_value

        response = self.resource.create()

        self.converter.encode.assert_called_once_with(expected_resource)
        url_for.assert_called_once_with('.get', resource_id=expected_resource.id)
        assert_that(response,
                    equal_to((expected_response,
                              201,
                              {'Location': expected_location,
                               'Content-Type': 'application/json'})))

    def test_when_edit_requested_then_resource_acquired_through_service(self, request, _):
        self.resource.edit(sentinel.resource_id)

        self.service.get.assert_called_once_with(sentinel.resource_id)

    def test_when_edit_requested_then_resource_updated(self, request, _):
        expected_resource = self.service.get.return_value

        self.resource.edit(sentinel.resource_id)
        self.converter.update.assert_called_once_with(request, expected_resource)

    def test_when_edit_requested_then_service_edits_resource(self, request, _):
        expected_resource = self.service.get.return_value

        self.resource.edit(sentinel.resource_id)

        self.service.edit.assert_called_once_with(expected_resource)

    def test_when_edit_requested_then_returns_empty_response(self, request, _):
        response = self.resource.edit(sentinel.resource_id)

        assert_that(response, equal_to(('', 204)))

    def test_when_delete_requested_then_resource_acquired_through_service(self, request, _):
        self.resource.delete(sentinel.resource_id)

        self.service.get.assert_called_once_with(sentinel.resource_id)

    def test_when_delete_requested_then_service_deletes_resource(self, request, _):
        expected_resource = self.service.get.return_value

        self.resource.delete(sentinel.resource_id)

        self.service.delete.assert_called_once_with(expected_resource)

    def test_when_delete_requested_then_returns_empty_response(self, request, _):
        response = self.resource.edit(sentinel.resource_id)

        assert_that(response, equal_to(('', 204)))


class TestCRUDService(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = Mock()
        self.notifier = Mock()
        self.service = CRUDService(self.dao, self.validator, self.notifier)

    def test_when_searching_then_dao_is_searched(self):
        parameters = {'param': 'value'}
        expected_search_result = self.dao.search.return_value

        result = self.service.search(parameters)

        self.dao.search.assert_called_once_with(**parameters)
        assert_that(result, equal_to(expected_search_result))

    def test_when_getting_then_resource_is_fetched_from_dao(self):
        expected_resource = self.dao.get.return_value

        result = self.service.get(sentinel.resource_id)

        self.dao.get.assert_called_once_with(sentinel.resource_id)
        assert_that(result, equal_to(expected_resource))

    def test_when_creating_then_resource_validated(self):
        self.service.create(sentinel.resource)

        self.validator.validate_create.assert_called_once_with(sentinel.resource)

    def test_when_creating_then_resource_created_with_dao(self):
        expected_resource = self.dao.create.return_value

        result = self.service.create(sentinel.resource)

        self.dao.create.assert_called_with(sentinel.resource)
        assert_that(result, equal_to(expected_resource))

    def test_when_creating_then_notifier_is_notified_using_resource(self):
        expected_resource = self.dao.create.return_value

        self.service.create(sentinel.resource)

        self.notifier.created.assert_called_once_with(expected_resource)

    def test_when_editing_then_resource_validated(self):
        self.service.edit(sentinel.resource)

        self.validator.validate_edit.assert_called_once_with(sentinel.resource)

    def test_when_editing_then_resource_edited_with_dao(self):
        self.service.edit(sentinel.resource)

        self.dao.edit.assert_called_with(sentinel.resource)

    def test_when_editing_then_notifier_is_notified_using_resource(self):
        self.service.edit(sentinel.resource)

        self.notifier.edited.assert_called_once_with(sentinel.resource)

    def test_when_deleting_then_resource_validated(self):
        self.service.delete(sentinel.resource)

        self.validator.validate_delete.assert_called_once_with(sentinel.resource)

    def test_when_deleting_then_resource_edited_with_dao(self):
        self.service.delete(sentinel.resource)

        self.dao.delete.assert_called_with(sentinel.resource)

    def test_when_deleting_then_notifier_is_notified_using_resource(self):
        self.service.delete(sentinel.resource)

        self.notifier.deleted.assert_called_once_with(sentinel.resource)


@patch('xivo_confd.helpers.resource.url_for')
@patch('xivo_confd.helpers.resource.request')
class TestAssociationResource(unittest.TestCase):

    def setUp(self):
        self.service = Mock()
        self.converter = Mock()
        self.resource = AssociationResource(self.service, self.converter)

    def test_when_listing_associations_then_service_called(self, request, url_for):
        self.resource.association_list(sentinel.parent_id)

        self.service.association_list.assert_called_once_with(sentinel.parent_id)

    def test_when_listing_associations_then_list_converted(self, request, url_for):
        expected_list = self.service.association_list.return_value
        expected_response = self.converter.encode_list.return_value

        result = self.resource.association_list(sentinel.parent_id)

        self.converter.encode_list.assert_called_once_with(expected_list)
        assert_that(result, equal_to((expected_response,
                                     200,
                                     {'Content-Type': 'application/json'})))

    def test_when_associating_resource_then_request_decoded(self, request, _):
        self.resource.associate(sentinel.parent_id)

        self.converter.decode.assert_called_once_with(request)

    def test_when_associating_resource_then_association_created(self, request, _):
        expected_association = self.converter.decode.return_value

        self.resource.associate(sentinel.parent_id)

        self.service.associate.assert_called_once_with(sentinel.parent_id, expected_association)

    def test_when_associating_then_association_encoded(self, request, url_for):
        expected_association = self.service.associate.return_value
        expected_response = self.converter.encode.return_value

        result = self.resource.associate(sentinel.parent_id)

        self.converter.encode.assert_called_once_with(expected_association)
        assert_that(result, equal_to((expected_response,
                                      201,
                                      {'Content-Type': 'application/json',
                                       'Location': url_for.return_value})))

    def test_when_dissociating_then_association_fetched_through_service(self, request, url_for):
        self.resource.dissociate(sentinel.parent_id, sentinel.resource_id)

        self.service.get_association.assert_called_once_with(sentinel.parent_id, sentinel.resource_id)

    def test_when_dissociating_then_service_called(self, request, url_for):
        expected_association = self.service.get_association.return_value

        result = self.resource.dissociate(sentinel.parent_id, sentinel.resource_id)

        self.service.dissociate.assert_called_once_with(expected_association)
        assert_that(result, equal_to(('', 204)))
