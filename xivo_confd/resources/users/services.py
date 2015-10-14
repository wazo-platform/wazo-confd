# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao
from xivo_dao.resources.func_key_template import dao as template_dao
from xivo_dao.resources.dial_action import dao as dial_action_dao
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.resources.users import notifier, validator
from xivo_confd.resources.func_key import services as func_key_service


def get_by_uuid(uuid):
    return user_dao.get_by_uuid(uuid)


def get(user_id):
    return user_dao.get(user_id)


def get_by_number_context(number, context):
    return user_dao.get_by_number_context(number, context)


def find_all(order=None):
    return user_dao.find_all(order=order)


def find_by_firstname_lastname(firstname, lastname):
    return user_dao.find_user(firstname, lastname)


def find_all_by_fullname(fullname):
    return user_dao.find_all_by_fullname(fullname)


def search(**parameters):
    return user_dao.search(**parameters)


def create(user):
    validator.validate_create(user)
    user = _create_user_in_database(user)
    notifier.created(user)
    return user


def _create_user_in_database(user):
    user.private_template_id = template_dao.create_private_template()

    if not user.caller_id:
        user.caller_id = u'"{}"'.format(user.fullname)

    user = user_dao.create(user)
    dial_action_dao.create_default_dial_actions_for_user(user)
    func_key_service.create_user_destination(user)
    return user


def edit(user):
    validator.validate_edit(user)
    user_dao.edit(user)
    notifier.edited(user)


def delete(user):
    validator.validate_delete(user)
    func_key_service.delete_user_destination(user)
    func_key_service.delete_bsfilter_destination(user)
    user_dao.delete(user)
    template_dao.delete_private_template(user.private_template_id)
    notifier.deleted(user)


def delete_voicemail(user):
    try:
        voicemail = voicemail_dao.get(user.voicemail_id)
    except NotFoundError:
        return
    else:
        voicemail_dao.delete(voicemail)
