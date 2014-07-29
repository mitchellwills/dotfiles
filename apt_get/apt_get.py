from __future__ import absolute_import
from dotfiles.module_base import *
import dotfiles.logger as logger


class AptGetRepository(ModuleBase):
    @before('AptGetUpdate')
    def do_install(self):
        if self.config.install and self.config.sudo:
            for repo in self.config.apt_get.repos:
                logger.call(['sudo', 'add-apt-repository', '-y', repo])
        else:
            logger.warning('not running add-apt-repository')

class AptGetUpdate(ModuleBase):
    @before('AptGetInstall')
    @before('AptGetUpgrade')
    def do_install(self):
        if self.config.install and self.config.update and self.config.sudo :
            logger.call(['sudo', 'apt-get', '-y', 'update'])
        else:
            logger.warning('not running apt-get update')

class AptGetUpgrade(ModuleBase):
    @before('AptGetInstall')
    def do_install(self):
        if self.config.install and self.config.upgrade and self.config.sudo:
            logger.call(['sudo', 'apt-get', '-y', 'dist-upgrade'])
        else:
            logger.warning('not running apt-get upgrade')


class AptGetInstall(ModuleBase):
    def do_install(self):
        if self.config.install and self.config.sudo:
            install_command = ['sudo', 'apt-get', 'install', '-y']
            install_command.extend(self.config.apt_get.install)
            logger.call(install_command)
        else:
            logger.warning('not running apt-get install')
