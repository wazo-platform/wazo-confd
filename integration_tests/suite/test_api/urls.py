class UrlFragment(object):

    @classmethod
    def root(cls, base=''):
        return cls([base])

    def __init__(self, fragments):
        self.fragments = fragments

    def __call__(self, fragment=None, p=None):
        return self._build(self._add(fragment, p))

    def __getattr__(self, name):
        return self._build(self._add(name))

    def __str__(self):
        return '/'.join(self.fragments)

    def __repr__(self):
        return "<{} '{}' {}>".format(self.__class__.__name__, str(self), self.fragments)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def apply(self, **kwargs):
        fragments = [f.format(**kwargs) for f in self.fragments]
        return self._build(fragments)

    def _build(self, fragments):
        return UrlFragment(fragments)

    def _add(self, fragment=None, p=None):
        if fragment and p:
            raise ValueError("fragment and param are mutually exclusive")
        if fragment:
            return self.fragments + [str(fragment)]
        if p:
            return self.fragments + ['{{{}}}'.format(p)]
        return self.fragments
