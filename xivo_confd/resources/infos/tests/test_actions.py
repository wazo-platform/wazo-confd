# -*- coding: UTF-8 -*-
#
# Copyright (C) 2014 Avencall
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

import uuid

from mock import patch

from xivo_confd.helpers.tests.test_resources import TestResources
from xivo_dao.data_handler.infos.model import Infos as InfosSchema


BASE_URL = "/1.1/infos"


class TestInfosAction(TestResources):

    def setUp(self):
        super(TestInfosAction, self).setUp()
        self.uuid = unicode(uuid.uuid5(uuid.NAMESPACE_DNS, __name__))
        self.infos = InfosSchema(uuid=self.uuid)

    def build_item(self, infos):
        item = {
            'uuid': infos.uuid
        }

        return item

    @patch('xivo_dao.data_handler.infos.services.get')
    def test_get(self, mock_infos_services_get):
        mock_infos_services_get.return_value = self.infos

        expected_result = self.build_item(self.infos)

        result = self.app.get(BASE_URL)

        self.assert_response_for_get(result, expected_result)
        mock_infos_services_get.assert_called_once_with()
