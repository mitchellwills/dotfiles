from __future__ import absolute_import
import os
from collections import OrderedDict
from module_base import *
import subprocess
import logger


class AptGetRepository(ModuleBase):
    @before('AptGetUpdate')
    def do_install(self):
        if self.config.install:
            for repo in self.config.apt_get.repos:
                with logger.trylog('Running add-apt-repository '+repo):
                    subprocess.call(['sudo', 'add-apt-repository', '-y', repo])
        else:
            logger.warning('not running add-apt-repository')

class AptGetUpdate(ModuleBase):
    @before('AptGetInstall')
    @before('AptGetUpgrade')
    def do_install(self):
        if self.config.install and self.config.update:
            with logger.trylog('Running apt-get update'):
                subprocess.call(['sudo', 'apt-get', '-y', 'update'])
        else:
            logger.warning('not running apt-get update')

class AptGetUpgrade(ModuleBase):
    @before('AptGetInstall')
    def do_install(self):
        if self.config.install and self.config.upgrade:
            with logger.trylog('Running apt-get upgrade'):
                subprocess.call(['sudo', 'apt-get', '-y', 'upgrade'])
        else:
            logger.warning('not running apt-get upgrade')


class AptGetInstall(ModuleBase):
    def do_install(self):
        if self.config.install:
            with logger.frame('apt-get installing ' + str(self.config.apt_get.install)):
                install_command = ['sudo', 'apt-get', 'install', '-q']
                install_command.extend(self.config.apt_get.install)
                subprocess.call(install_command)
        else:
            logger.warning('not running apt-get install')
