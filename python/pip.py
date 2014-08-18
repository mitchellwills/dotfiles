from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.src_package import *
import dotfiles.logger as logger



class PipActionFactory(PackageActionFactory):
    def name(self):
        return 'pip'

    def install(self, packages):
        if self.config.local:
            raise Exception('cannot install pip package without sudo')
        command = ['sudo', 'pip', 'install']
        command.extend(packages)
        return [CommandAction(command)]



@abstract
@depends('pip')
class PipPackage(PackageBase):
    def __init__(self, package):
        self.package = package

    def name(self):
        return 'pip:'+self.package

    def install(self):
        return self.action('pip').install([self.package])

class PipPackageFactory(PackageFactory):
    def name(self):
        return 'pip'

    def build(self, name):
        return PipPackage(name)
