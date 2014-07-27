from __future__ import absolute_import
from dotfiles.module_base import *
from dotfiles.src_package import *
import dotfiles.logger as logger

class InstallNpm(ModuleBase):
    def do_config(self):
        self.config.bash.add('path', ['~/local/bin'], 0)

    @after('InstallNode')
    def do_install(self):
        if self.config.install and self.config.node.install:
            package = SrcPackage('npm', GitRepo('https://github.com/npm/npm.git', 'v1.4.21'), self)
            package.update()
            package.configure('~/local')
            package.make_install()

class NpmUpdate(ModuleBase):
    @after('InstallNpm')
    def do_install(self):
        if self.config.install and self.config.node.install and self.config.upgrade:
            logger.call(['npm', 'update', '-g'])

class NpmInstall(ModuleBase):
    @after('NpmUpdate')
    def do_install(self):
        if self.config.install and self.config.node.install:
            for package in self.config.node.npm.install:
                logger.call(['npm', 'install', '-g', package])
