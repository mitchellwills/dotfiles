from __future__ import absolute_import
import os
from dotfiles.package_base import *
from dotfiles.util import *
import dotfiles.logger as logger
from dotfiles.actions import *
import glob

@suggests('emacs-conf')
@suggests('emacs:haskell-mode')
@suggests('emacs:flycheck')
@suggests('apt-get:yaml-mode')
class emacs(PackageBase):
    def already_installed(self):
        try:
            return subprocess.call(['emacs', '--version']) == 0
        except OSError:
            return False
    def install(self):
        if self.config.local:
            if self.already_installed():
                logger.log('Installing local, but detected emacs already installed', verbose = True)
                return []
            else:
                raise Exception('cannot install emacs locally')
        else:
            return self.action('apt-get').install(['emacs'])


class EmacsActionFactory(PackageActionFactory):
    def name(self):
        return 'emacs'

    def update(self):
        return [CommandAction(['emacs', '--batch', '-l', self.home_file('.emacs'), '--eval', '(package-refresh-contents)'], deps=['emacs', 'emacs-conf'])]

    def install(self, packages):
        commands = []
        for package in packages:
            commands.append(CommandAction(['emacs', '--batch', '-l', self.home_file('.emacs'), '--eval', '(package-install \''+package+')'], deps=['emacs', 'emacs-conf']))
        return commands

@abstract
@depends('emacs-conf')
@depends('emacs')
class EmacsPackage(PackageBase):
    def __init__(self, package):
        self.package = package

    def name(self):
        return 'emacs:'+self.package

    def install(self):
        return concat_lists(
            self.action('emacs').update(),
            self.action('emacs').install([self.package])
        )

class EmacsPackageFactory(PackageFactory):
    def name(self):
        return 'emacs'

    def build(self, name):
        return EmacsPackage(name)
