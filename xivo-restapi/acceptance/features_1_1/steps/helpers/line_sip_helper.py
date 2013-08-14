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

from remote import remote_exec


def delete_all():
    remote_exec(_delete_all)


def _delete_all(channel):
    from xivo_dao.data_handler.line import services as line_services
    from xivo_dao.data_handler.user_line_extension import services as ule_services

    all_ules = ule_services.find_all()

    for line in line_services.find_all():

        ules = [u for u in all_ules if u.line_id == line.id]
        for ule in ules:
            ule_services.delete(ule)

        line_services.delete(line)


def create_line_sip(parameters):
    remote_exec(_create_line_sip, parameters=parameters)


def _create_line_sip(channel, parameters):
    from xivo_dao.data_handler.line import services as line_services
    from xivo_dao.data_handler.line.model import LineSIP

    line = LineSIP(**parameters)
    line_services.create(line)
