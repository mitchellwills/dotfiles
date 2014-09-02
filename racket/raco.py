from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.src_package import *
from dotfiles.actions import *
from dotfiles.util import *
import dotfiles.logger as logger

class RacketActionFactory(PackageActionFactory):
    def name(self):
        return 'raco'

    def install(self, packages):
        commands = []
        for package in packages:
            commands.append(CommandAction(['raco', 'pkg', 'install', package], deps=['racket']))
        return commands

@abstract
class RacoPackage(PackageBase):
    def __init__(self, package):
        self.package = package

    def name(self):
        return 'raco:'+self.package

    def install(self):
        return self.action('raco').install([self.package])

class RacoPackageFactory(PackageFactory):
    def name(self):
        return 'raco'

    def build(self, name):
        return RacoPackage(name)
