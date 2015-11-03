# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from werkzeug.local import LocalProxy
from xivo_confd.application import app
from xivo_confd.application import api
from xivo_confd.application import auth
from xivo_confd.application import create_app
from xivo_confd.application import get_bus_publisher
from xivo_confd.application import get_sysconfd_publisher

bus = LocalProxy(get_bus_publisher)
sysconfd = LocalProxy(get_sysconfd_publisher)
