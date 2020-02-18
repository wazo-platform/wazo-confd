# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os


class FileSystemClient:
    def __init__(self, execute, base_path):
        self.base_path = base_path
        self.execute = execute

    def create_directory(self, name, mode='777'):
        self.execute(
            [
                'install',
                '-dm{mode}'.format(mode=mode),
                os.path.join(self.base_path, name),
            ]
        )

    def create_file(self, name, content='content', mode='666'):
        self.execute(
            [
                'sh',
                '-c',
                'echo -n {content} > {path}'.format(
                    content=content, path=os.path.join(self.base_path, name)
                ),
            ]
        )
        self.execute(['chmod', mode, os.path.join(self.base_path, name)])

    def move_file(self, old_name, new_name):
        self.execute(
            [
                'mv',
                os.path.join(self.base_path, old_name),
                os.path.join(self.base_path, new_name),
            ]
        )


class TenantFileSystemClient:
    def __init__(self, execute, base_path):
        self.base_path = base_path
        self.execute = execute

    def create_directory(self, tenant_uuid, name, mode='777'):
        self.execute(
            [
                'install',
                '-dm{mode}'.format(mode=mode),
                os.path.join(self.base_path, 'tenants', tenant_uuid, name),
            ]
        )

    def create_file(self, tenant_uuid, name, content='content', mode='666'):
        self.execute(
            [
                'sh',
                '-c',
                'echo -n {content} > {path}'.format(
                    content=content,
                    path=os.path.join(self.base_path, 'tenants', tenant_uuid, name),
                ),
            ]
        )
        self.execute(['chmod', mode, os.path.join(self.base_path, name)])
