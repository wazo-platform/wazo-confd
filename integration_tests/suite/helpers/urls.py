# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class UrlFragment:
    @classmethod
    def root(cls, base=''):
        return cls([base])

    def __init__(self, fragments):
        self.fragments = fragments

    def __call__(self, fragment):
        return self._copy()._add(fragment)

    def __getattr__(self, fragment):
        return self._copy()._add(fragment)

    def __str__(self):
        return '/'.join(self.fragments)

    def __repr__(self):
        return "<{} '{}' {}>".format(self.__class__.__name__, str(self), self.fragments)

    def __enter__(self):
        return self._copy()

    def __exit__(self, *args):
        pass

    def _add(self, fragment):
        fragment = str(fragment)
        # If a fragment is a python keyword (ex: global) it can be suffixed by a '_'
        if fragment.endswith('_'):
            fragment = fragment[:-1]
        self.fragments.append(fragment)
        return self

    def _copy(self):
        return self.__class__(list(self.fragments))
