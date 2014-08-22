from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.actions import *
from dotfiles.util import *
import dotfiles.logger as logger


class AptGet(PackageBase):
    def name(self):
        return 'apt-get'

    def install(self):
        if self.config.local:
            raise Exception('apt-get is not usable for local only installs')
        return []

class AptGetActionFactory(PackageActionFactory):
    def name(self):
        return 'apt-get'

    def install(self, packages):
        command = ['sudo', 'apt-get', 'install', '-y']
        command.extend(packages)
        return [CommandAction(command, deps=['apt-get'])]

    def add_repo(self, repo):
        return [CommandAction(['sudo', 'add-apt-repository', '-y', repo], deps=['apt-get'])]

    def update(self):
        return [CommandAction(['sudo', 'apt-get', 'update'], deps=['apt-get'])]

    def upgrade(self):
        return [CommandAction(['sudo', 'apt-get', 'upgrade'], deps=['apt-get'])]

@abstract
class AptGetPackage(PackageBase):
    def __init__(self, package):
        self.package = package

    def name(self):
        return 'apt-get:'+self.package

    def install(self):
        return self.action('apt-get').install([self.package])

class AptGetPackageFactory(PackageFactory):
    def name(self):
        return 'apt-get'

    def build(self, name):
        return AptGetPackage(name)
