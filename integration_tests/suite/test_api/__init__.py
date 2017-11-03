# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
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


from . import mocks
from xivo_test_helpers.confd import (
    SingletonProxy,
    associations,
    bus,
    confd,
    config,
    db,
    errors,
    fixtures,
    helpers,
    new_confd,
    scenarios,
)

__all__ = [
    associations,
    bus,
    confd,
    config,
    db,
    errors,
    fixtures,
    helpers,
    scenarios,
    mocks,
]
confd_csv = SingletonProxy(new_confd, {'Accept': 'text/csv; charset=utf-8'})
