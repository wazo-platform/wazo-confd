# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


class FileSystemClient(object):

    def __init__(self, execute, base_path):
        self.base_path = base_path
        self.execute = execute
        self.create_directory(base_path)

    def create_directory(self, name, mode='777'):
        self.execute([
            'mkdir',
            '-p',
            '{base_path}/{name}'.format(base_path=self.base_path, name=name)
        ])
        self.execute([
            'chmod',
            '{mode}',
            '{base_path}/{name}'.format(mode=mode, base_path=self.base_path, name=name)
        ])

    def create_file(self, name, content='content', mode='666'):
        self.execute([
            'sh',
            '-c',
            'echo -n {content} > {base_path}/{name}'.format(
                content=content,
                base_path=self.base_path,
                name=name
            )
        ])
        self.execute([
            'chmod',
            '{mode}',
            '{base_path}/{name}'.format(mode=mode, base_path=self.base_path, name=name)
        ])
