from dotfiles.util import *
from dotfiles.src_package import *
from dotfiles.module_base import *
import logger

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


class SudoAndLocalPackageBase(PackageBase):
    def __init__(self, sudo_package, local_package):
        PackageBase.__init__(self)
        self.sudo_package = sudo_package
        self.local_package = local_package

    def init_package(self, context):
        PackageBase.init_package(self, context)
        if self.config.local:
            self.sudo_package.init_package(context)
        else:
            self.local_package.init_package(context)

    def install(self):
        if self.config.install_local:
            return self.local_package.install()
        else:
            return self.sudo_package.install()

class AptGetPackageBase(PackageBase):
    def __init__(self, package, name = None):
        PackageBase.__init__(self)
        self.package_name = None
        if type(package) is str:
            self.package = [package]
            if name is None:
                self.package_name = package
        elif type(package) is list:
            self.package = package
        else:
            raise Exception('Unknown package set')

    def name(self):
        if self.package_name is None:
            return PackageBase.name(self)
        return self.package_name

    def install(self):
        if not self.config.local:
            raise Exception('cannot install apt-get package without sudo')
        else:
            return self.action('apt-get').install(package)

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

def depends(spec):
    def wrap(func):
        if not hasattr(func, 'deps'):
            func.deps = set()
        func.deps.add(spec)
        return func
    return wrap
