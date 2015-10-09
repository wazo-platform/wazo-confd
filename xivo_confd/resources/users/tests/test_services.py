# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from hamcrest import assert_that, equal_to
from mock import patch, Mock, sentinel as s

from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_case import TestCase
from xivo_dao.resources.user.model import User

from xivo_confd.resources.users import services as user_services


class TestGetUser(TestCase):

    @patch('xivo_dao.resources.user.dao.get')
    def test_get(self, user_dao_get):
        user_id = 123
        expected_result = User(id=user_id)
        user_dao_get.return_value = User(id=user_id)

        result = user_services.get(user_id)

        user_dao_get.assert_called_once_with(user_id)
        assert_that(result, equal_to(expected_result))

    @patch('xivo_dao.resources.user.dao.get_by_number_context')
    def test_get_by_number_context(self, user_dao_get):
        number, context = '9876', 'default'
        user_id = 123
        expected_result = User(id=user_id)
        user_dao_get.return_value = User(id=user_id)

        result = user_services.get_by_number_context(number, context)

        user_dao_get.assert_called_once_with(number, context)
        assert_that(result, equal_to(expected_result))

    @patch('xivo_dao.resources.user.dao.get_by_uuid')
    def test_get_by_uuid(self, user_dao_get_by_uuid):
        result = user_services.get_by_uuid(s.uuid)

        user_dao_get_by_uuid.assert_called_once_with(s.uuid)
        assert_that(result, equal_to(user_dao_get_by_uuid.return_value))


class TestSearchUser(TestCase):

    @patch('xivo_dao.resources.user.dao.search')
    def test_search(self, user_dao_search):
        search_result = user_dao_search.return_value = Mock(SearchResult)

        result = user_services.search(search='toto',
                                      order='firstname',
                                      direction='desc',
                                      limit=1,
                                      skip=2)

        assert_that(result, equal_to(search_result))
        user_dao_search.assert_called_once_with(search='toto',
                                                order='firstname',
                                                direction='desc',
                                                limit=1,
                                                skip=2)


class TestFindUser(TestCase):

    @patch('xivo_dao.resources.user.dao.find_all')
    def test_find_all(self, user_dao_find_all):
        first_user = Mock(User)
        second_user = Mock(User)
        expected_order = None

        expected = [first_user, second_user]

        user_dao_find_all.return_value = expected

        result = user_services.find_all()

        self.assertEquals(result, expected)

        user_dao_find_all.assert_called_once_with(order=expected_order)

    @patch('xivo_dao.resources.user.dao.find_all')
    def test_find_all_order_by_lastname(self, user_dao_find_all):
        first_user = Mock(User)
        second_user = Mock(User)
        expected_order = ['lastname']

        expected = [first_user, second_user]

        user_dao_find_all.return_value = expected

        result = user_services.find_all(order=['lastname'])

        self.assertEquals(result, expected)

        user_dao_find_all.assert_called_once_with(order=expected_order)

    @patch('xivo_dao.resources.user.dao.find_user')
    def test_find_user(self, user_dao_find_user):
        user = Mock(User)
        firstname = 'Lord'
        lastname = 'Sanderson'

        user_dao_find_user.return_value = user

        result = user_services.find_by_firstname_lastname(firstname, lastname)

        self.assertEquals(result, user)
        user_dao_find_user.assert_called_once_with(firstname, lastname)

    @patch('xivo_dao.resources.user.dao.find_all_by_fullname')
    def test_find_all_by_fullname(self, user_dao_find_all_by_fullname):
        fullname = 'Lord Sanderson'

        user = Mock(User)
        user.firstname = 'Lord'
        user.lastname = 'Sanderson'

        expected_result = [user]

        user_dao_find_all_by_fullname.return_value = [user]

        result = user_services.find_all_by_fullname(fullname)

        self.assertEquals(expected_result, result)
        user_dao_find_all_by_fullname.assert_called_once_with(fullname)


@patch('xivo_confd.resources.func_key.services.create_user_destination')
@patch('xivo_dao.resources.dial_action.dao.create_default_dial_actions_for_user')
@patch('xivo_dao.resources.func_key_template.dao.create_private_template')
@patch('xivo_confd.resources.users.notifier.created')
@patch('xivo_dao.resources.user.dao.create')
@patch('xivo_confd.resources.users.validator.validate_create')
class TestCreate(TestCase):

    def test_create(self,
                    user_validate_create,
                    user_dao_create,
                    user_notifier_created,
                    create_private_template,
                    create_default_dial_actions_for_user,
                    create_user_destination):
        firstname = u'Clémence'
        lastname = u'Dupont'
        caller_id = u'"Clémence Dupont"'
        user = User(firstname=firstname,
                    lastname=lastname,
                    caller_id=caller_id)

        user_dao_create.return_value = user

        result = user_services.create(user)

        user_validate_create.assert_called_once_with(user)
        user_dao_create.assert_called_once_with(user)
        user_notifier_created.assert_called_once_with(user)
        create_default_dial_actions_for_user.assert_called_once_with(user)
        create_user_destination.assert_called_once_with(user)

        self.assertEquals(type(result), User)
        self.assertEquals(result.private_template_id, create_private_template.return_value)

    def test_given_no_caller_id_when_creating_a_user_then_generates_a_caller_id(self,
                                                                                user_validate_create,
                                                                                user_dao_create,
                                                                                user_notifier_created,
                                                                                create_private_template,
                                                                                create_default_dial_actions_for_user,
                                                                                create_user_destination):
        firstname = u'Clémence'
        lastname = u'Dupont'
        caller_id = u'"Clémence Dupont"'

        user = User(firstname=firstname, lastname=lastname)
        expected_user = User(firstname=firstname,
                             lastname=lastname,
                             caller_id=caller_id,
                             private_template_id=create_private_template.return_value)

        user_services.create(user)

        user_dao_create.assert_called_once_with(expected_user)


class TestEdit(TestCase):

    @patch('xivo_confd.resources.users.notifier.edited')
    @patch('xivo_dao.resources.user.dao.edit')
    @patch('xivo_confd.resources.users.validator.validate_edit')
    def test_edit(self,
                  user_validate_edit,
                  user_dao_edit,
                  user_notifier_edited):
        user = User(id=1, firstname='user', lastname='toto')

        user_services.edit(user)

        user_validate_edit.assert_called_once_with(user)
        user_dao_edit.assert_called_once_with(user)
        user_notifier_edited.assert_called_once_with(user)


class TestDelete(TestCase):

    @patch('xivo_dao.resources.func_key_template.dao.delete_private_template')
    @patch('xivo_confd.resources.users.notifier.deleted')
    @patch('xivo_dao.resources.user.dao.delete')
    @patch('xivo_confd.resources.func_key.services.delete_bsfilter_destination')
    @patch('xivo_confd.resources.func_key.services.delete_user_destination')
    @patch('xivo_confd.resources.users.validator.validate_delete')
    def test_delete(self,
                    user_validate_delete,
                    delete_user_destination,
                    delete_bsfilter_destination,
                    user_dao_delete,
                    user_notifier_deleted,
                    delete_private_template):
        user = User(id=1, firstname='user', lastname='toto', private_template_id=10)

        user_services.delete(user)

        user_validate_delete.assert_called_once_with(user)
        user_dao_delete.assert_called_once_with(user)
        delete_user_destination.assert_called_once_with(user)
        delete_bsfilter_destination.assert_called_once_with(user)
        user_notifier_deleted.assert_called_once_with(user)
        delete_private_template.assert_called_once_with(user.private_template_id)
