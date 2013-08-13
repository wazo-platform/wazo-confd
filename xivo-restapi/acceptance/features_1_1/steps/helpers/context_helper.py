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


def create_context(context_name):
    remote_exec(_create_context, name=context_name)


def _create_context(channel, name):
    from xivo_dao.data_handler.context import services as context_services
    from xivo_dao.data_handler.context.model import Context, ContextType

    existing_context = context_services.find_by_name(name)
    if not existing_context:
        context = Context(name=name, display_name=name, type=ContextType.internal)
        context_services.create(context)
