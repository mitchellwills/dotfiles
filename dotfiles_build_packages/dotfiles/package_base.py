from dotfiles.src_package import *
from dotfiles.module_base import *
import logger

class PackageBase(ModuleBase):
    def __init__(self, context):
        ModuleBase.__init__(self, context)

    def name(self):
        return type(self).__name__

    def do_install(self):
        self.install_package()

    def install_package(self):
        logger.failed('No install for '+self.name())


class SudoPackageBase(PackageBase):
    def __init__(self, context):
        PackageBase.__init__(self, context)
    def install_package(self):
        if self.config.sudo:
            self.install_sudo()
        else:
            self.install_local()
    def install_sudo(self):
        logger.failed('No sudo install for '+self.name())
    def install_local(self):
        logger.failed('No local install for '+self.name())


class SrcConfigureMakeInstallPackage(PackageBase):
    def __init__(self, context, pkg_name, repo):
        PackageBase.__init__(self, context)
        self.pkg_name = pkg_name
        self.repo = repo
    def name(self):
        return self.pkg_name

    def do_config(self):
        self.config.bash.add('path', [os.path.join(os.path.expanduser(self.config.local_install.dir), 'bin')], 0)
    def install_package(self):
        package = SrcPackage(self.pkg_name, self.repo, self)
        package.update()
        package.configure(os.path.expanduser(self.config.local_install.dir))
        package.make_install()

