from __future__ import absolute_import
import os
from collections import OrderedDict
from install_util import *
from module_base import *
import subprocess


class AptGetUpdate(ModuleBase):
    @before('AptGetInstall')
    @before('AptGetUpgrade')
    def do_install(self):
        if self.config.install and self.config.update:
            with logger.trylog('Running apt-get update'):
                subprocess.call(['sudo', 'apt-get', '-y', 'update'])

class AptGetUpgrade(ModuleBase):
    @before('AptGetInstall')
    def do_install(self):
        if self.config.install and self.config.upgrade:
            with logger.trylog('Running apt-get upgrade'):
                subprocess.call(['sudo', 'apt-get', '-y', 'upgrade'])


class AptGetInstall(ModuleBase):
    def do_install(self):
        if self.config.install:
            with logger.frame('apt-get installing ' + str(self.config.apt_get.install)):
                install_command = ['sudo', 'apt-get', 'install']
                install_command.extend(self.config.apt_get.install)
                subprocess.call(install_command)
