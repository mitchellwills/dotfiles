from __future__ import absolute_import
from dotfiles.module_base import *
from dotfiles.package_base import *
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
        if self.config.local:
            raise Exception('cannot install apt-get package without sudo')
        command = ['sudo', 'apt-get', 'install', '-y']
        command.extend(packages)
        return [CommandAction(command)]

    def add_repo(self, repo):
        if self.config.local:
            raise Exception('cannot install add-apt-repository for local only installs')
        return [CommandAction(['sudo', 'add-apt-repository', '-y', repo])]

    def update(self):
        if self.config.local:
            raise Exception('cannot install apt-get update for local only installs')
        return [CommandAction(['sudo', 'apt-get', 'update'])]

    def upgrade(self):
        if self.config.local:
            raise Exception('cannot install apt-get upgrade for local only installs')
        return [CommandAction(['sudo', 'apt-get', 'upgrade'])]

@abstract
@depends('apt-get')
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
