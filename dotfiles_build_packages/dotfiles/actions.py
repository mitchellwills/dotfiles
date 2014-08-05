import logger


class PackageActionFactory(object):
    def __init__(self):
        self.context = None

    def init_factory(self, context):
        self.context = context

    def __getattr__(self, name):
        if self.context is None:
            raise Exception('Action Factory not yet initialized')
        return getattr(self.context, name)


class CommandAction(object):
    def __init__(self, command):
        self.command = command

    def __call__(self):
        logger.call(self.command)
