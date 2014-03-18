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

from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_restapi.v1_0.service_data_model.line_sdm import LineSdm
from xivo_restapi.v1_0.mapping_alchemy_sdm.abstract_mapping import AbstractMapping


class LineMapping(AbstractMapping):

    # mapping = {alchemy_field: sdm_field}
    mapping = {'number': 'number'
               }

    reverse_mapping = dict([[v, k] for k, v in mapping.items()])

    alchemy_default_values = {}

    alchemy_types = {}

    sdm_types = {}

    def __init__(self):
        self.sdm_class = LineSdm
        self.alchemy_class = LineFeatures
