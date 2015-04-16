# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from mock import patch, Mock
from hamcrest import assert_that, equal_to, contains, none

from xivo_dao.tests.test_case import TestCase
from xivo_dao.resources.user_line.model import UserLine
from xivo_dao.resources.line_extension.model import LineExtension
from xivo_dao.resources.user.model import User
from xivo_dao.resources.line.model import Line
from xivo_dao.resources.extension.model import Extension
from xivo_dao.resources.user_line_extension import services as ule_service


@patch('xivo_dao.resources.user_line_extension.services.fix_associations')
@patch('xivo_dao.resources.user_line.dao.find_main_user_line')
@patch('xivo_dao.resources.user_line.dao.associate')
class TestAssociateUserLine(TestCase):

    def test_given_user_and_line_associated_then_associations_get_fixed(self,
                                                                        user_line_associate,
                                                                        find_main_user_line,
                                                                        fix_associations):
        user_line = Mock(UserLine)
        created_user_line = user_line_associate.return_value = Mock(UserLine, user_id=1, line_id=2)
        main_user_line = find_main_user_line.return_value = Mock(UserLine, user_id=3, line_id=2)

        result = ule_service.associate_user_line(user_line)

        assert_that(result, equal_to(created_user_line))
        find_main_user_line.assert_called_once_with(created_user_line.line_id)
        fix_associations.assert_called_once_with(main_user_line)


@patch('xivo_dao.resources.user_line_extension.services.fix_associations')
@patch('xivo_dao.resources.user_line.dao.find_main_user_line')
@patch('xivo_dao.resources.line_extension.dao.associate')
class TestAssociateLineExtension(TestCase):

    def test_given_main_user_associated_then_associations_get_fixed(self,
                                                                    line_extension_associate,
                                                                    find_main_user_line,
                                                                    fix_associations):
        line_extension = Mock(LineExtension)
        created_line_extension = line_extension_associate.return_value = Mock(LineExtension, line_id=1, extension_id=2)
        main_user_line = find_main_user_line.return_value = Mock(UserLine, user_id=3, line_id=1)

        result = ule_service.associate_line_extension(line_extension)

        assert_that(result, equal_to(created_line_extension))
        find_main_user_line.assert_called_once_with(created_line_extension.line_id)
        fix_associations.assert_called_once_with(main_user_line)

    def test_given_no_main_user_then_no_associations_fixed(self,
                                                           line_extension_associate,
                                                           find_main_user_line,
                                                           fix_associations):
        line_extension = Mock(LineExtension)
        created_line_extension = line_extension_associate.return_value = Mock(LineExtension, line_id=1, extension_id=2)
        find_main_user_line.return_value = None

        result = ule_service.associate_line_extension(line_extension)

        assert_that(result, equal_to(created_line_extension))
        find_main_user_line.assert_called_once_with(created_line_extension.line_id)
        self.assertNotCalled(fix_associations)


@patch('xivo_dao.resources.user_line_extension.services.update_resources')
@patch('xivo_dao.resources.user_line_extension.services.find_resources')
class TestFixAssociations(TestCase):

    def test_given_main_user_line_then_resources_updated(self,
                                                         find_resources,
                                                         update_resources):
        main_user_line = Mock(UserLine)
        main_user, line, extension = find_resources.return_value = (Mock(User), Mock(Line), Mock(Extension))

        ule_service.fix_associations(main_user_line)

        find_resources.assert_called_once_with(main_user_line)
        update_resources.assert_called_once_with(main_user, line, extension)


@patch('xivo_dao.resources.user_line_extension.services.find_extension')
@patch('xivo_dao.resources.line.dao.get')
@patch('xivo_dao.resources.user.dao.get')
class TestFindResources(TestCase):

    def test_given_main_user_line_then_returns_user_line_and_extension(self,
                                                                       user_dao_get,
                                                                       line_dao_get,
                                                                       find_extension):
        main_user_line = Mock(UserLine, user_id=1, line_id=2)
        main_user = user_dao_get.return_value = Mock(User)
        line = line_dao_get.return_value = Mock(Line)
        extension = find_extension.return_value = Mock(Extension)

        result = ule_service.find_resources(main_user_line)

        assert_that(result, contains(main_user, line, extension))
        user_dao_get.assert_called_once_with(main_user_line.user_id)
        line_dao_get.assert_called_once_with(main_user_line.line_id)
        find_extension.assert_called_once_with(main_user_line.line_id)


@patch('xivo_dao.resources.extension.dao.get')
@patch('xivo_dao.resources.line_extension.dao.find_by_line_id')
class TestFindExtension(TestCase):

    def test_given_no_extension_then_returns_none(self, find_by_line_id, extension_get):
        line_id = 1
        find_by_line_id.return_value = None

        result = ule_service.find_extension(line_id)

        assert_that(result, none())

    def test_given_extension_associated_then_returns_extension(self, find_by_line_id, extension_get):
        line_id = 1
        find_by_line_id.return_value = Mock(LineExtension, extension_id=1)
        extension = extension_get.return_value = Mock(Extension)

        result = ule_service.find_extension(line_id)

        assert_that(result, equal_to(extension))


@patch('xivo_dao.resources.user_line_extension.services.update_exten_and_context')
@patch('xivo_dao.resources.user_line_extension.services.update_line')
@patch('xivo_dao.resources.user_line_extension.services.update_caller_id')
class TestUpdateResources(TestCase):

    def test_given_no_extension_then_updates_caller_id_and_line(self,
                                                                update_caller_id,
                                                                update_line,
                                                                update_exten_and_context):
        main_user = Mock(User)
        line = Mock(Line)

        ule_service.update_resources(main_user, line)

        update_caller_id.assert_called_once_with(main_user, line, None)
        update_line.assert_called_once_with(main_user, line)
        self.assertNotCalled(update_exten_and_context)

    def test_given_extension_associated_then_updates_all_resources(self,
                                                                   update_caller_id,
                                                                   update_line,
                                                                   update_exten_and_context):
        main_user = Mock(User)
        line = Mock(Line)
        extension = Mock(Extension)

        ule_service.update_resources(main_user, line, extension)

        update_caller_id.assert_called_once_with(main_user, line, extension)
        update_line.assert_called_once_with(main_user, line)
        update_exten_and_context.assert_called_once_with(main_user, line, extension)


@patch('xivo_dao.resources.line.dao.edit')
@patch('xivo.caller_id.assemble_caller_id')
class TestUpdateCallerId(TestCase):

    def test_given_no_extension_then_callerid_contains_only_user_name(self,
                                                                      assemble_caller_id,
                                                                      line_dao_edit):
        main_user = Mock(User, firstname="firstname")
        line = Mock(Line)
        callerid = assemble_caller_id.return_value = Mock()

        ule_service.update_caller_id(main_user, line)

        assert_that(line.callerid, equal_to(callerid))
        assemble_caller_id.assert_called_once_with(main_user.fullname, None)
        line_dao_edit.assert_called_once_with(line)

    def test_given_extension_associated_then_callerid_contains_user_name_and_extension(self,
                                                                                       assemble_caller_id,
                                                                                       line_dao_edit):
        main_user = Mock(User, firstname="firstname")
        line = Mock(Line)
        extension = Mock(Extension, exten="1000")
        callerid = assemble_caller_id.return_value = Mock()

        ule_service.update_caller_id(main_user, line, extension)

        assert_that(line.callerid, equal_to(callerid))
        assemble_caller_id.assert_called_once_with(main_user.fullname, extension.exten)
        line_dao_edit.assert_called_once_with(line)


@patch('xivo_dao.resources.line.dao.update_xivo_userid')
class TestUpdateLine(TestCase):

    def test_given_main_user_and_line_then_user_id_updated(self, update_xivo_userid):
        main_user = Mock(User)
        line = Mock(Line)

        ule_service.update_line(main_user, line)

        update_xivo_userid.assert_called_once_with(line, main_user)


@patch('xivo_dao.resources.extension.dao.associate_destination')
@patch('xivo_dao.resources.line.dao.associate_extension')
class TestExtenAndContext(TestCase):

    def test_given_main_user_line_and_extension_then_exten_and_context_updated(self,
                                                                               line_associate_extension,
                                                                               extension_associate_destination):
        main_user = Mock(User, id=1)
        line = Mock(Line, id=2)
        extension = Mock(Extension, id=3)

        ule_service.update_exten_and_context(main_user, line, extension)

        extension_associate_destination.assert_called_once_with(extension.id, 'user', main_user.id)
        line_associate_extension.assert_called_once_with(extension, line.id)


@patch('xivo_dao.resources.user_line_extension.services.remove_exten_and_context')
@patch('xivo_dao.resources.extension.dao.get')
@patch('xivo_dao.resources.line_extension.dao.dissociate')
class TestDissociateLineExtension(TestCase):

    def test_given_dissociated_line_extension_then_exten_and_context_removed(self,
                                                                             line_extension_dissociate,
                                                                             extension_dao_get,
                                                                             remove_exten_and_context):
        line_extension = Mock(LineExtension, extension_id=1)
        extension = extension_dao_get.return_value = Mock(Extension)

        ule_service.dissociate_line_extension(line_extension)

        line_extension_dissociate.assert_called_once_with(line_extension)
        extension_dao_get.assert_called_once_with(line_extension.extension_id)
        remove_exten_and_context.assert_called_once_with(extension)


@patch('xivo_dao.resources.extension.dao.dissociate_extension')
@patch('xivo_dao.resources.line.dao.dissociate_extension')
class TestRemoveExtenAndContext(TestCase):

    def test_given_extension_then_exten_and_context_removed(self,
                                                            line_dissociate_extension,
                                                            ext_dissociate_extension):
        extension = Mock(Extension, id=1)

        ule_service.remove_exten_and_context(extension)

        line_dissociate_extension.assert_called_once_with(extension)
        ext_dissociate_extension.assert_called_once_with(extension.id)


@patch('xivo_dao.resources.user_line_extension.services.fix_main_user_dissociation')
@patch('xivo_dao.resources.user_line.dao.dissociate')
class TestDissociateUserLine(TestCase):

    def test_given_secondary_user_then_only_user_line_dissociated(self,
                                                                  user_line_dissociate,
                                                                  fix_main_user_dissociation):
        user_line = Mock(UserLine, line_id=1, main_user=False)

        ule_service.dissociate_user_line(user_line)

        user_line_dissociate.assert_called_once_with(user_line)
        self.assertNotCalled(fix_main_user_dissociation)

    def test_given_main_user_then_dissociation_gets_fixed(self,
                                                          user_line_dissociate,
                                                          fix_main_user_dissociation):
        user_line = Mock(UserLine, line_id=1, main_user=True)

        ule_service.dissociate_user_line(user_line)

        user_line_dissociate.assert_called_once_with(user_line)
        fix_main_user_dissociation.assert_called_once_with(user_line.line_id)


@patch('xivo_dao.resources.user_line_extension.services.remove_exten_and_context')
@patch('xivo_dao.resources.user_line_extension.services.find_extension')
@patch('xivo_dao.resources.user_line_extension.services.remove_caller_id')
class TestFixMainUserDissociation(TestCase):

    def test_given_no_extension_associated_then_caller_id_removed(self,
                                                                  remove_caller_id,
                                                                  find_extension,
                                                                  remove_exten_and_context):
        line_id = 1
        find_extension.return_value = None

        ule_service.fix_main_user_dissociation(line_id)

        remove_caller_id.assert_called_once_with(line_id)
        find_extension.assert_called_once_with(line_id)
        self.assertNotCalled(remove_exten_and_context)

    def test_given_extension_associated_then_caller_id_and_exten_removed(self,
                                                                         remove_caller_id,
                                                                         find_extension,
                                                                         remove_exten_and_context):
        line_id = 1
        extension = find_extension.return_value = Mock(Extension)

        ule_service.fix_main_user_dissociation(line_id)

        remove_caller_id.assert_called_once_with(line_id)
        find_extension.assert_called_once_with(line_id)
        remove_exten_and_context.assert_called_once_with(extension)


@patch('xivo_dao.resources.line.dao.delete_user_references')
class TestRemoveCallerId(TestCase):

    def test_given_dissociate_line_then_removes_user_caller_id(self,
                                                               delete_user_references):
        line_id = 1

        ule_service.remove_caller_id(line_id)

        delete_user_references.assert_called_once_with(line_id)
