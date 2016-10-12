# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from .notifier import build_notifier


class OutcallTrunkService(object):

    def __init__(self, notifier):
        self.notifier = notifier

    def associate_all_trunks(self, outcall, trunks):
        outcall.trunks = trunks
        self.notifier.associated_all_trunks(outcall, trunks)


def build_service():
    return OutcallTrunkService(build_notifier())
