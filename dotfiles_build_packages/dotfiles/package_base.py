from dotfiles.util import *
from dotfiles.src_package import *
from dotfiles.module_base import *
import logger


def suggests(spec):
    def wrap(func):
        if not hasattr(func, 'suggests'):
            func.suggests = set()
        func.suggests.add(spec)
        return func
    return wrap

def abstract(func):
    func.abstract = True
    return func

def depends(spec):
    def wrap(func):
        if not hasattr(func, 'deps'):
            func.deps = set()
        func.deps.add(spec)
        return func
    return wrap

def configures(spec):
    def wrap(func):
        if not hasattr(func, 'configures'):
            func.configures = set()
        func.configures.add(spec)
        return func
    return wrap


class PackageFactory(object):
    pass

class PackageBase(object):
    def __init__(self):
        self.context = None

    def init_package(self, context):
        self.context = context

    def __getattr__(self, name):
        if self.context is None:
            raise Exception('Package not yet initialized')
        return getattr(self.context, name)

    def name(self):
        return type(self).__name__

    def __str__(self):
        return 'package('+self.name()+')'
    def __name__(self):
        return self.__str__()
    def __repr__(self):
        return self.__str__()

    def install(self):
        logger.failed('No install for '+self.name())
        return None

class SrcConfigureMakeInstallPackage(PackageBase):
    def __init__(self, pkg_name, repo):
        PackageBase.__init__(self)
        self.pkg_name = pkg_name
        self.repo = repo

    def name(self):
        return self.pkg_name

    def install(self):
        package = SrcPackage(self.pkg_name, self.repo, self)
        return self.action('src').update_configure_make_install(package)


