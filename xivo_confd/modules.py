import abc

class BasePlugin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load(self, app):
        pass

    def unload(self):
        pass
