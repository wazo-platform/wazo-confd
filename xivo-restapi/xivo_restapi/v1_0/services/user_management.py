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

import logging

from provd.rest.client.client import new_provisioning_client
from urllib2 import URLError
from xivo_dao import user_dao, line_dao, device_dao, voicemail_dao
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.user_line_extension import dao as user_line_extension_dao
from xivo_dao.data_handler.user_line_extension import services as user_line_extension_services
from xivo_restapi import config
from xivo_restapi.v1_0.restapi_config import RestAPIConfig
from xivo_restapi.v1_0.services.utils.exceptions import NoSuchElementException, \
    ProvdError, VoicemailExistsException, SysconfdError
from xivo_restapi.v1_0.services.utils.sysconfd_connector import SysconfdConnector
from xivo_restapi.v1_0.services.voicemail_management import VoicemailManagement
from xivo_restapi.v1_0.mapping_alchemy_sdm.user_mapping import UserMapping
from xivo_restapi.v1_0.mapping_alchemy_sdm.line_mapping import LineMapping

data_access_logger = logging.getLogger(config.DATA_ACCESS_LOGGERNAME)


class UserManagement(object):

    def __init__(self):
        self.user_mapping = UserMapping()
        self.line_mapping = LineMapping()
        self.voicemail_manager = VoicemailManagement()
        self.provisioning_client = new_provisioning_client(RestAPIConfig.PROVD_URL)
        self.device_manager = self.provisioning_client.device_manager()
        self.config_manager = self.provisioning_client.config_manager()
        self.sysconfd_connector = SysconfdConnector()

    def get_all_users(self):
        users_lines = user_dao.get_all_join_line()
        return_list = []
        for user, line in users_lines:
            result_user = self.user_mapping.alchemy_to_sdm(user)
            if line is not None:
                result_user.line = self.line_mapping.alchemy_to_sdm(line)
            return_list.append(result_user)
        return return_list

    def get_user(self, userid):
        user = None
        line = None
        result = user_dao.get_user_join_line(userid)
        if result is None:
            raise NoSuchElementException("No such user")
        else:
            user, line = result

        result = self.user_mapping.alchemy_to_sdm(user)
        if line is not None:
            result.line = self.line_mapping.alchemy_to_sdm(line)
        return result

    def create_user(self, user):
        data_access_logger.info("Creating a user with the data %s." % user.todict())
        if user.description is None:
            user.description = ''
        user_interne = self.user_mapping.sdm_to_alchemy(user)
        user_dao.add_user(user_interne)

    def edit_user(self, userid, data):
        data_access_logger.info("Editing the user of id %s with data %s."
                                % (userid, data))
        alchemy_data = self.user_mapping.sdm_to_alchemy_dict(data)
        updated_rows = user_dao.update(userid, alchemy_data)
        if updated_rows == 0:
            raise NoSuchElementException("No such user")
        if 'lastname' not in data and 'firstname' not in data:
            return
        voicemailid = user_dao.get(userid).voicemailid
        if voicemailid is not None:
            fullname = user_dao.get(userid).fullname
            self.voicemail_manager.edit_voicemail(voicemailid, {'fullname': fullname})

    def delete_user(self, userid, delete_voicemail=False):
        data_access_logger.info("Deleting the user of id %s" % userid)
        try:
            user = user_services.get(userid)
        except ElementNotExistsError:
            raise NoSuchElementException("No such user: " + str(userid))
        self._remove_voicemail(user, delete_voicemail)
        self._remove_lines(user)
        user_services.delete(user)

    def _remove_lines(self, user):
        associations = user_line_extension_services.find_all_by_user_id(user.id)
        for association in associations:
            self._remove_association(association)

    def _remove_association(self, association):
        user_line_extension_dao.delete(association)
        line = line_dao.get(association.line_id)
        self._remove_line(line)

    def _remove_line(self, line):
        device = line.device
        line_dao.delete(line.id)
        deviceid = device_dao.get_deviceid(device)
        if deviceid is not None:
            try:
                self._provd_remove_line(deviceid, line.num)
            except URLError as e:
                raise ProvdError(str(e))

    def _provd_remove_line(self, deviceid, linenum):
        config = self.config_manager.get(deviceid)
        del config["raw_config"]["sip_lines"][str(linenum)]
        if len(config["raw_config"]["sip_lines"]) == 0:
            # then we reset to autoprov
            self._reset_config(config)
            self._reset_device_to_autoprov(deviceid)
        self.config_manager.update(config)

    def _reset_config(self, config):
        del config["raw_config"]["sip_lines"]
        if "funckeys" in config["raw_config"]:
            del config["raw_config"]["funckeys"]

    def _reset_device_to_autoprov(self, deviceid):
        device = self.device_manager.get(deviceid)
        new_configid = self.config_manager.autocreate()
        device["config"] = new_configid
        self.device_manager.update(device)

    def _remove_voicemail(self, user, delete_voicemail):
        voicemailid = user.voicemail_id
        if voicemailid and not delete_voicemail:
            raise VoicemailExistsException()
        if voicemailid:
            self._delete_voicemail(voicemailid)

    def _delete_voicemail(self, voicemailid):
        voicemail = voicemail_dao.get(voicemailid)
        context, mailbox = voicemail.context, voicemail.mailbox
        voicemail_dao.delete(voicemailid)
        try:
            self.sysconfd_connector.delete_voicemail_storage(context, mailbox)
        except Exception as e:
            raise SysconfdError(str(e))
