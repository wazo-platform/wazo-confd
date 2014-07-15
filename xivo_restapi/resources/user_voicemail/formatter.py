# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


from xivo_restapi.resources.user_voicemail import mapper
from xivo_dao.data_handler.user_voicemail.model import UserVoicemail
from xivo_restapi.helpers import serializer

from xivo_restapi.helpers.formatter import Formatter


class UserVoicemailFormatter(Formatter):

    def __init__(self):
        Formatter.__init__(self, mapper, serializer, UserVoicemail)

    def dict_to_model(self, api_data, user_id):
        model = Formatter.dict_to_model(self, api_data)
        model.user_id = user_id
        return model
