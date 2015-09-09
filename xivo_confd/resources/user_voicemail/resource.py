# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_confd.helpers.resource import SingleAssociationResource, build_response


class UserVoicemailResource(SingleAssociationResource):

    def list_associations_by_child(self, voicemail_id):
        self.service.validate_resource(voicemail_id)
        associations = self.service.list_by_child(voicemail_id)
        response = self.converter.encode_list(associations)
        return build_response(response)
