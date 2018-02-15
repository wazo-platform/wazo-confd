# -*- coding: UTF-8 -*-

"""Plugin that offers no configuration service and serves TFTP/HTTP requests
in its var/tftpboot directory.

"""

__version__ = "$Revision: 10355 $ $Date: 2011-03-08 14:38:11 -0500 (Tue, 08 Mar 2011) $"
__license__ = """
    Copyright (C) 2010  Proformatique <technique@proformatique.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from provd.plugins import StandardPlugin
from provd.servers.http import HTTPNoListingFileService
from provd.servers.tftp.service import TFTPFileService


class ZeroPlugin(StandardPlugin):
    IS_PLUGIN = True
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        self.tftp_service = TFTPFileService(self._tftpboot_dir)
        self.http_service = HTTPNoListingFileService(self._tftpboot_dir)
