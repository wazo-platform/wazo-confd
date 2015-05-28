# -*- coding: UTF-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import abc


class FuncKeyTemplate(object):

    def __init__(self, name, keys=None, description=None, id=None):
        self.id = id
        self.name = name
        self.description = description
        self.keys = keys or {}

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("'cannot compare '{}' and '{}'".format(self.__class__,
                                                                   other.__class__))
        return all([self.id == other.id,
                    self.name == other.name,
                    self.description == other.description,
                    self.keys == other.keys])


class FuncKey(object):

    def __init__(self, position, destination, label=None, blf=False, id=None):
        self.id = id
        self.position = position
        self.destination = destination
        self.label = label
        self.blf = blf

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("'cannot compare '{}' and '{}'".format(self.__class__,
                                                                   other.__class__))
        return all([self.id == other.id,
                    self.position == other.position,
                    self.destination == other.destination,
                    self.label == other.label,
                    self.blf == other.blf])
