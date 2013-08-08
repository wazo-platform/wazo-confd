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

from helpers import device_helper
from lettuce import step


@step(u'Given I have no devices')
def given_there_are_no_devices(step):
    device_helper.delete_all()


@step(u'Given I only have the following devices:')
def given_there_are_the_following_devices(step):
    device_helper.delete_all()
    for deviceinfo in step.hashes:
        device_helper.create_device(deviceinfo)
