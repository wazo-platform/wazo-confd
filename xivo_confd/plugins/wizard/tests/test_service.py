# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

import unittest

from mock import Mock, patch, mock_open
from hamcrest import assert_that, equal_to, empty, none
from textwrap import dedent

from xivo_confd.plugins.wizard.service import WizardService


class TestWizardService(unittest.TestCase):

    def setUp(self):
        self.service = WizardService(Mock(), Mock(), Mock(), Mock(), Mock())

    @patch('xivo_confd.plugins.wizard.service.netifaces')
    def test_get_interfaces(self, netifaces):
        netifaces.interfaces.return_value = ['eth0']
        netifaces.AF_INET = 4
        netifaces.ifaddresses.return_value = {
            4: [{'addr': '192.168.0.1', 'netmask': '255.255.0.0'}]
        }
        expected_result = [{'ip_address': '192.168.0.1', 'netmask': '255.255.0.0', 'interface': 'eth0'}]

        result = self.service.get_interfaces()

        assert_that(result, equal_to(expected_result))

    @patch('xivo_confd.plugins.wizard.service.netifaces')
    def test_get_interfaces_do_not_return_lo_interface(self, netifaces):
        netifaces.interfaces.return_value = ['eth0', 'lo']
        netifaces.AF_INET = 4
        netifaces.ifaddresses.return_value = {
            4: [{'addr': '192.168.0.1', 'netmask': '255.255.0.0'}]
        }
        expected_result = [{'ip_address': '192.168.0.1', 'netmask': '255.255.0.0', 'interface': 'eth0'}]

        result = self.service.get_interfaces()

        assert_that(result, equal_to(expected_result))

    @patch('xivo_confd.plugins.wizard.service.netifaces')
    def test_get_interfaces_return_empty_list_when_no_ip_address(self, netifaces):
        netifaces.interfaces.return_value = ['eth0']
        netifaces.AF_INET = 4
        netifaces.ifaddresses.return_value = {}

        result = self.service.get_interfaces()

        assert_that(result, empty())

    @patch('xivo_confd.plugins.wizard.service.netifaces')
    def test_get_gateways(self, netifaces):
        netifaces.AF_INET = 4
        netifaces.gateways.return_value = {4: [('192.168.2.0', 'eth0'), ('192.168.32.0', 'eth1')]}
        expected_result = [{'gateway': '192.168.2.0', 'interface': 'eth0'},
                           {'gateway': '192.168.32.0', 'interface': 'eth1'}]

        result = self.service.get_gateways()

        assert_that(result, equal_to(expected_result))

    @patch('xivo_confd.plugins.wizard.service.netifaces')
    def test_get_gateways_return_empty_list_when_no_gateways(self, netifaces):
        netifaces.AF_INET = 4
        netifaces.gateways.return_value = {}

        result = self.service.get_gateways()

        assert_that(result, empty())

    def test_get_timezone(self):
        with patch('xivo_confd.plugins.wizard.service.open', mock_open(read_data='America/Montreal'), create=True) as mopen:
            result = self.service.get_timezone()

        mopen.assert_called_once_with('/etc/timezone', 'r')
        assert_that(result, equal_to('America/Montreal'))

    @patch('xivo_confd.plugins.wizard.service.open', create=True)
    def test_get_timezone_return_none_if_no_file(self, mopen):
        mopen.side_effect = IOError()
        result = self.service.get_timezone()

        assert_that(result, none())

    def test_get_nameservers(self):
        resolv_conf = dedent('''
            search example.com
            nameserver 192.168.2.0
            nameserver 192.168.2.1''')
        expected_result = ['192.168.2.0', '192.168.2.1']
        with patch('xivo_confd.plugins.wizard.service.open', mock_open(read_data=resolv_conf), create=True) as mopen:
            result = self.service.get_nameservers()

        mopen.assert_called_once_with('/etc/resolv.conf', 'r')
        assert_that(result, equal_to(expected_result))

    @patch('xivo_confd.plugins.wizard.service.open', create=True)
    def test_get_nameservers_return_none_if_no_file(self, mopen):
        mopen.side_effect = IOError()
        result = self.service.get_nameservers()

        assert_that(result, empty())

    @patch('xivo_confd.plugins.wizard.service.socket')
    def test_get_hostname(self, socket):
        socket.gethostname.return_value = 'confd'
        expected_result = 'confd'

        result = self.service.get_hostname()
        assert_that(result, equal_to(expected_result))

    @patch('xivo_confd.plugins.wizard.service.socket')
    def test_get_hostname_return_only_hostname_when_fqdn(self, socket):
        socket.gethostname.return_value = 'confd.example.com'
        expected_result = 'confd'

        result = self.service.get_hostname()
        assert_that(result, equal_to(expected_result))

    @patch('xivo_confd.plugins.wizard.service.socket')
    def test_get_domain(self, socket):
        socket.getfqdn.return_value = 'confd.example.com'
        expected_result = 'example.com'

        result = self.service.get_domain()
        assert_that(result, equal_to(expected_result))

    @patch('xivo_confd.plugins.wizard.service.socket')
    def test_get_domain_return_none_when_no_domain(self, socket):
        socket.getfqdn.return_value = 'confd'

        result = self.service.get_domain()
        assert_that(result, none())
