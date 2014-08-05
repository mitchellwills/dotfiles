from __future__ import absolute_import
from dotfiles.module_base import *
from dotfiles.package_base import *
import dotfiles.logger as logger


class AptGetActionFactory(PackageActionFactory):
    def name(self):
        return 'apt-get'

    def install(self, packages):
        command = ['sudo', 'apt-get', 'install', '-y']
        command.extend(packages)
        return [CommandAction(packages)]

    def update(self, packages):
        return [CommandAction(['sudo', 'apt-get', 'update'])]

    def upgrade(self, packages):
        return [CommandAction(['sudo', 'apt-get', 'upgrade'])]

