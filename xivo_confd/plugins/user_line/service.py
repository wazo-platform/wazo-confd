# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.user_line import dao as user_line_dao

from .notifier import build_notifier
from .validator import build_validator


class UserLineService:

    def __init__(self, dao, validator, notifier):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier

    def find_all_by(self, **criteria):
        return self.dao.find_all_by(**criteria)

    def find_by(self, **criteria):
        return self.dao.find_by(**criteria)

    def get(self, user, line):
        return self.dao.get_by(user_id=user.id, line_id=line.id)

    def associate(self, user, line):
        if line in user.lines:
            return self.dao.get_by(user_id=user.id, line_id=line.id)

        self.validator.validate_association(user, line)
        user_line = self.dao.associate(user, line)
        self.notifier.associated(user_line)
        return user_line

    def dissociate(self, user, line):
        user_line = self.dao.find_by(user_id=user.id, line_id=line.id)
        if not user_line:
            return

        self.validator.validate_dissociation(user, line)
        self.notifier.dissociated(user_line)
        self.dao.dissociate(user, line)

    def associate_all_lines(self, user, lines):
        if len(lines) != len(set(lines)):
            raise errors.not_permitted('Cannot associate same line more than once')

        for existing_line in user.lines:
            if existing_line not in lines:
                self.validator.validate_dissociation(user, existing_line)

        for line in lines:
            if line not in user.lines:
                self.validator.validate_association(user, line)

        for existing_line in user.lines:
            if existing_line not in lines:
                user_line = self.find_by(user_id=user.id, line_id=existing_line.id)
                self.notifier.dissociated(user_line)

        user_lines = self.dao.associate_all_lines(user, lines)

        for user_line in user_lines:
            self.notifier.associated(user_line)


def build_service():
    return UserLineService(user_line_dao,
                           build_validator(),
                           build_notifier())
