from __future__ import absolute_import
from dotfiles.module_base import *
from dotfiles.package_base import *
import dotfiles.logger as logger

@after('NodePackage')
class NpmPackage(SrcConfigureMakeInstallPackage):
    def __init__(self, context):
        SrcConfigureMakeInstallPackage.__init__(self, context, 'npm', GitRepo('https://github.com/npm/npm.git', 'v1.4.21'))

class NpmUpdate(ModuleBase):
    @after('NpmPackage')
    def do_install(self):
        if self.config.install and self.config.node.install and self.config.upgrade:
            logger.call(['npm', 'update', '-g'])

class NpmInstall(ModuleBase):
    @after('NpmUpdate')
    def do_install(self):
        if self.config.install and self.config.node.install:
            for package in self.config.node.npm.install:
                logger.call(['npm', 'install', '-g', package])
