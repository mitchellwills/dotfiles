from __future__ import absolute_import
from dotfiles.package_base import *
import dotfiles.logger as logger

@depends('node')
class npm(SrcConfigureMakeInstallPackage):
    def __init__(self):
        SrcConfigureMakeInstallPackage.__init__(self, 'npm', GitRepo('https://github.com/npm/npm.git', 'v1.4.21'))

class NpmActionFactory(PackageActionFactory):
    def name(self):
        return 'npm'

    def install(self, packages):
        commands = []
        for package in packages:
            commands.append(CommandAction(['npm', 'install', '-g', package], deps=['npm']))
        return commands

@abstract
class NpmPackage(PackageBase):
    def __init__(self, package):
        self.package = package

    def name(self):
        return 'npm:'+self.package

    def install(self):
        return self.action('npm').install([self.package])

class NpmPackageFactory(PackageFactory):
    def name(self):
        return 'npm'

    def build(self, name):
        return NpmPackage(name)
