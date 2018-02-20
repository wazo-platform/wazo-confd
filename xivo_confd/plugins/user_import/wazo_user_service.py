# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .auth_client import auth_client


class WazoUserService(object):

    def __init__(self, auth_client):
        self._auth_client = auth_client

    def create(self, user):
        self._auth_client.new_user(
            uuid=user.get('uuid'),
            firstname=user.get('firstname'),
            lastname=user.get('lastname'),
            email_address=user.get('email_address'),
            username=user.get('username') or user.get('email_address') or user.get('uuid'),
            password=user.get('password'),
        )

    def update(self, user):
        self._auth_client.edit_user(user['uuid'], **user)
        if user.get('password'):
            self._auth_client.users.set_password(user['uuid'], user['password'])
        if user.get('emails'):
            self._auth_client.admin.update_user_emails(user['uuid'], user['emails'])


def build_service():
    return WazoUserService(auth_client)
