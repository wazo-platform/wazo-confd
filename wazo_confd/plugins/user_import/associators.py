# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import abc

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.helpers.exception import NotFoundError


class Associator(metaclass=abc.ABCMeta):
    def __init__(self, service):
        self.service = service

    @abc.abstractmethod
    def associate(self, entry):
        return

    @abc.abstractmethod
    def update(self, entry):
        return


# WazoUser need to be an associator to have the user uuid
class WazoUserAssociator(Associator):
    def associate(self, entry):
        user = entry.get_resource('user')
        wazo_user = entry.get_resource('wazo_user')
        wazo_user['uuid'] = user.uuid
        return self.service.create(wazo_user)

    def update(self, entry):
        pass


class LineAssociator(Associator):
    def associate(self, entry):
        user = entry.get_resource('user')
        line = entry.get_resource('line')
        if user and line:
            self.service.associate(user, line)

    def update(self, entry):
        user = entry.get_resource('user')
        line = entry.get_resource('line')
        if user and line and not self.associated(user, line):
            self.service.associate(user, line)

    def associated(self, user, line):
        return self.service.find_by(user_id=user.id, line_id=line.id) is not None


class ExtensionAssociator(Associator):
    def associate(self, entry):
        line = entry.get_resource('line')
        extension = entry.get_resource('extension')
        if line and extension:
            self.service.associate(line, extension)

    def update(self, entry):
        line = entry.get_resource('line')
        extension = entry.get_resource('extension')
        if line and extension and not self.associated(line, extension):
            self.service.associate(line, extension)

    def associated(self, line, extension):
        try:
            self.service.get(line, extension)
        except NotFoundError:
            return False
        return True


class SipAssociator(Associator):
    def associate(self, entry):
        line = entry.get_resource('line')
        sip = entry.get_resource('sip') or entry.get_resource('webrtc')
        if line and sip:
            self.service.associate(line, sip)

    def update(self, entry):
        line = entry.get_resource('line')
        sip = entry.get_resource('sip')
        if line and sip and not line.is_associated_with(sip):
            self.service.associate(line, sip)


class SccpAssociator(Associator):
    def associate(self, entry):
        line = entry.get_resource('line')
        sccp = entry.get_resource('sccp')
        if line and sccp:
            self.service.associate(line, sccp)

    def update(self, entry):
        line = entry.get_resource('line')
        sccp = entry.get_resource('sccp')
        if line and sccp and not line.is_associated_with(sccp):
            self.service.associate(line, sccp)


class VoicemailAssociator(Associator):
    def associate(self, entry):
        user = entry.get_resource('user')
        voicemail = entry.get_resource('voicemail')
        if user and voicemail:
            self.service.associate(user, voicemail)

    def update(self, entry):
        user = entry.get_resource('user')
        voicemail = entry.get_resource('voicemail')
        if user and voicemail and not self.associated(user, voicemail):
            self.service.associate(user, voicemail)

    def associated(self, user, voicemail):
        return (
            self.service.find_by(user_id=user.id, voicemail_id=voicemail.id) is not None
        )


class IncallAssociator(Associator):
    def associate(self, entry):
        incall = entry.get_resource('incall')
        extension = entry.get_resource('extension_incall')
        if incall and extension:
            self.service.associate(incall, extension)
            self.update_destination(entry)

    def update_destination(self, entry):
        ring_seconds = entry.extract_field('incall', 'ring_seconds')
        user = entry.get_resource('user')
        incall = entry.get_resource('incall')
        incall.destination = Dialaction(
            action='user',
            actionarg1=str(user.id),
            actionarg2=str(ring_seconds) if ring_seconds else None,
        )

    def update(self, entry):
        incall = entry.get_resource('incall')
        extension = entry.get_resource('extension_incall')
        if incall and extension and not self.associated(incall, extension):
            self.service.associate(incall, extension)
        if incall:
            self.update_destination(entry)

    def associated(self, incall, extension):
        try:
            self.service.get(incall, extension)
        except NotFoundError:
            return False
        return True


class CallPermissionAssociator(Associator):
    def __init__(self, service, call_permission_service):
        super().__init__(service)
        self.call_permission_service = call_permission_service

    def associate(self, entry):
        user = entry.get_resource('user')
        permissions = entry.get_resource('call_permissions')
        if permissions is not None:
            self.associate_permissions(user, permissions)

    def associate_permissions(self, user, permissions):
        self.service.dissociate_all_by_user(user)
        for permission in permissions:
            self.service.associate(user, permission)

    def update(self, entry):
        user = entry.get_resource('user')
        names = entry.extract_field('call_permissions', 'names')
        if names is not None:
            entry.call_permissions = [
                self.call_permission_service.get_by(name=name) for name in names
            ]
            self.associate_permissions(user, entry.call_permissions)
