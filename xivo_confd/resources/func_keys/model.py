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


from xivo_dao.helpers.new_model import NewModel


class Model(NewModel):

    _RELATION = {}


class FuncKeyTemplate(Model):

    FIELDS = ['id',
              'name',
              'description',
              'keys']

    MANDATORY = ['name']


class FuncKey(Model):

    FIELDS = ['id',
              'position',
              'destination',
              'label',
              'blf']

    MANDATORY = ['position',
                 'destination']


class UserDestination(Model):

    FIELDS = ['user_id']

    MANDATORY = ['user_id']


class GroupDestination(Model):

    FIELDS = ['group_id']

    MANDATORY = ['group_id']


class QueueDestination(Model):

    FIELDS = ['queue_id']

    MANDATORY = ['queue_id']


class ConferenceDestination(Model):

    FIELDS = ['conference_id']

    MANDATORY = ['conference_id']


class PagingDestination(Model):

    FIELDS = ['paging_id']

    MANDATORY = ['paging_id']


class BSFilterDestination(Model):

    FIELDS = ['filter_member_id']

    MANDATORY = ['filter_member_id']


class CustomDestination(Model):

    FIELDS = ['exten']

    MANDATORY = ['exten']


class ServiceDestination(Model):

    FIELDS = ['service']

    MANDATORY = ['service']


class ForwardDestination(Model):

    FIELDS = ['forward', 'exten']

    MANDATORY = ['forward', 'exten']


class TransferDestination(Model):

    FIELDS = ['transfer', 'exten']

    MANDATORY = ['forward', 'exten']


class AgentDestination(Model):

    FIELDS = ['action', 'agent_id']

    MANDATORY = ['action', 'agent_id']


class ParkPositionDestination(Model):

    FIELDS = ['position']

    MANDATORY = ['position']


class ParkingDestination(Model):

    FIELDS = []

    MANDATORY = []
