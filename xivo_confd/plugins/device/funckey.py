# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import abc

from xivo.xivo_helpers import fkey_extension
from xivo_dao.resources.line import dao as line_dao_module
from xivo_dao.resources.user_line import dao as user_line_dao_module
from xivo_dao.resources.line_extension import dao as line_extension_dao_module
from xivo_dao.resources.extension import dao as extension_dao_module
from xivo_dao.resources.features import dao as features_dao_module
from xivo_dao.resources.paging import dao as paging_dao_module


def build_converters():
    return {
        'agent': AgentConverter(extension_dao_module),
        'bsfilter': BSFilterConverter(extension_dao_module),
        'conference': ConferenceConverter(extension_dao_module),
        'custom': CustomConverter(),
        'forward': ForwardConverter(extension_dao_module),
        'group': GroupConverter(extension_dao_module),
        'onlinerec': OnlineRecordingConverter(features_dao_module),
        'paging': PagingConverter(extension_dao_module, paging_dao_module),
        'park_position': ParkPositionConverter(),
        'parking': ParkingConverter(features_dao_module),
        'queue': QueueConverter(extension_dao_module),
        'service': ServiceConverter(extension_dao_module),
        'transfer': TransferConverter(features_dao_module),
        'user': UserConverter(line_dao_module,
                              user_line_dao_module,
                              line_extension_dao_module,
                              extension_dao_module),
    }


class FuncKeyConverter(object):

    __metaclass__ = abc.ABCMeta

    INVALID_CHARS = "\n\r\t;"

    @abc.abstractmethod
    def build(self, user, line, position, funckey):
        return

    def provd_funckey(self, line, position, funckey, value):
        label = self.remove_invalid_chars(funckey.label or '')
        value = self.remove_invalid_chars(value)
        return {position: {
            'label': label,
            'line': line.device_slot,
            'type': self.determine_type(funckey),
            'value': value}}

    def determine_type(self, funckey):
        return 'blf' if funckey.blf else 'speeddial'

    def progfunckey(self, prog_exten, user_id, exten, argument):
        return fkey_extension(prog_exten, [user_id, exten, argument])

    def remove_invalid_chars(self, text):
        for char in self.INVALID_CHARS:
            text = text.replace(char, "")
        return text


class UserConverter(FuncKeyConverter):

    def __init__(self, line_dao, user_line_dao, line_extension_dao, extension_dao):
        self.line_dao = line_dao
        self.user_line_dao = user_line_dao
        self.line_extension_dao = line_extension_dao
        self.extension_dao = extension_dao

    def build(self, user, line, position, funckey):
        funckey_line = self.find_user_line(funckey.destination.user_id)
        if not funckey_line:
            return {}

        extension = self.find_extension(funckey_line)
        if not extension:
            return {}

        return self.provd_funckey(line, position, funckey, extension.exten)

    def find_user_line(self, user_id):
        user_lines = self.user_line_dao.find_all_by_user_id(user_id)
        main_users = [ul for ul in user_lines if ul.main_user]

        if not main_users:
            return None

        return self.line_dao.get(main_users[0].line_id)

    def find_extension(self, line):
        line_extension = self.line_extension_dao.find_by_line_id(line.id)
        if not line_extension:
            return None

        return self.extension_dao.get(line_extension.extension_id)


class GroupConverter(FuncKeyConverter):

    def __init__(self, extension_dao):
        self.extension_dao = extension_dao

    def build(self, user, line, position, funckey):
        extension = self.extension_dao.get_by(type='group', typeval=str(funckey.destination.group_id))
        return self.provd_funckey(line, position, funckey, extension.exten)

    def determine_type(self, funckey):
        return 'speeddial'


class QueueConverter(FuncKeyConverter):

    def __init__(self, extension_dao):
        self.extension_dao = extension_dao

    def build(self, user, line, position, funckey):
        extension = self.extension_dao.get_by(type='queue', typeval=str(funckey.destination.queue_id))
        return self.provd_funckey(line, position, funckey, extension.exten)

    def determine_type(self, funckey):
        return 'speeddial'


class ConferenceConverter(FuncKeyConverter):

    def __init__(self, extension_dao):
        self.extension_dao = extension_dao

    def build(self, user, line, position, funckey):
        extension = self.extension_dao.get_by(type='meetme', typeval=str(funckey.destination.conference_id))
        return self.provd_funckey(line, position, funckey, extension.exten)


class PagingConverter(FuncKeyConverter):

    def __init__(self, extension_dao, paging_dao):
        self.extension_dao = extension_dao
        self.paging_dao = paging_dao

    def build(self, user, line, position, funckey):
        prefix_exten = self.extension_dao.get_by(type='extenfeatures', typeval='paging')
        extension = self.paging_dao.get(funckey.destination.paging_id).number
        value = '{}{}'.format(prefix_exten.clean_exten(), extension)
        return self.provd_funckey(line, position, funckey, value)

    def determine_type(self, funckey):
        return 'speeddial'


class ServiceConverter(FuncKeyConverter):

    PROGFUNCKEYS = ('callrecord',
                    'incallfilter',
                    'enablednd',
                    'enablevm')

    def __init__(self, extension_dao):
        self.extension_dao = extension_dao

    def build(self, user, line, position, funckey):
        extension = self.extension_dao.get(funckey.destination.extension_id)

        if funckey.destination.service in self.PROGFUNCKEYS:
            prog_exten = self.extension_dao.get_by(type='extenfeatures', typeval='phoneprogfunckey')
            value = self.progfunckey(prog_exten.exten,
                                     user.id,
                                     extension.clean_exten(),
                                     None)
        else:
            value = extension.clean_exten()

        return self.provd_funckey(line, position, funckey, value)

    def determine_type(self, funckey):
        if funckey.blf and funckey.destination.service in self.PROGFUNCKEYS:
            return 'blf'
        return 'speeddial'


class CustomConverter(FuncKeyConverter):

    def build(self, user, line, position, funckey):
        return self.provd_funckey(line, position, funckey, funckey.destination.exten)


class ForwardConverter(FuncKeyConverter):

    def __init__(self, extension_dao):
        self.extension_dao = extension_dao

    def build(self, user, line, position, funckey):
        prog_exten = self.extension_dao.get_by(type='extenfeatures', typeval='phoneprogfunckey')
        fwd_exten = self.extension_dao.get(funckey.destination.extension_id)

        value = self.progfunckey(prog_exten.exten,
                                 user.id,
                                 fwd_exten.exten,
                                 funckey.destination.exten)

        return self.provd_funckey(line, position, funckey, value)


class TransferConverter(FuncKeyConverter):

    def __init__(self, features_dao):
        self.features_dao = features_dao

    def build(self, user, line, position, funckey):
        exten = self.features_dao.get_value(funckey.destination.feature_id)
        return self.provd_funckey(line, position, funckey, exten)


class ParkPositionConverter(FuncKeyConverter):

    def build(self, user, line, position, funckey):
        return self.provd_funckey(line,
                                  position,
                                  funckey,
                                  str(funckey.destination.position))


class ParkingConverter(FuncKeyConverter):

    def __init__(self, features_dao):
        self.features_dao = features_dao

    def build(self, user, line, position, funckey):
        exten = self.features_dao.get_value(funckey.destination.feature_id)
        return self.provd_funckey(line, position, funckey, exten)

    def determine_type(self, funckey):
        return 'park'


class BSFilterConverter(FuncKeyConverter):

    def __init__(self, extension_dao):
        self.extension_dao = extension_dao

    def build(self, user, line, position, funckey):
        prefix = self.extension_dao.get_by(type='extenfeatures', typeval='bsfilter')

        value = '{}{}'.format(prefix.clean_exten(),
                              funckey.destination.filter_member_id)

        return self.provd_funckey(line, position, funckey, value)


class AgentConverter(FuncKeyConverter):

    def __init__(self, extension_dao):
        self.extension_dao = extension_dao

    def build(self, user, line, position, funckey):
        prog_exten = self.extension_dao.get_by(type='extenfeatures', typeval='phoneprogfunckey')
        action_exten = self.extension_dao.get(funckey.destination.extension_id)

        value = self.progfunckey(prog_exten.exten,
                                 user.id,
                                 action_exten.exten,
                                 '*{}'.format(funckey.destination.agent_id))

        return self.provd_funckey(line, position, funckey, value)


class OnlineRecordingConverter(FuncKeyConverter):

    def __init__(self, features_dao):
        self.features_dao = features_dao

    def build(self, user, line, position, funckey):
        exten = self.features_dao.get_value(funckey.destination.feature_id)
        return self.provd_funckey(line, position, funckey, exten)

    def determine_type(self, funckey):
        return 'speeddial'
