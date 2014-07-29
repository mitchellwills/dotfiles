from __future__ import absolute_import
from dotfiles.module_base import *
from dotfiles.src_package import *
import dotfiles.logger as logger


class InstallPip(ModuleBase):
    def do_config(self):
        if self.config.sudo:
            self.config.apt_get.add('install', ['python-pip'], 0)
    def do_install(self):
        if self.config.install and not self.config.sudo:
            logger.failed('could not install pip without sudo')

class PipInstall(ModuleBase):
    @after('AptGetInstall')
    def do_install(self):
        if self.config.install and self.config.sudo:
            if self.config.python.pip.install:
                install_command = []
                if self.config.sudo:
                    install_command.append('sudo')
                else:
                    logger.failed('could not install pip packages because install without sudo not supported')
                install_command.extend(['pip', 'install'])
                if self.config.upgrade:
                    install_command.append('--upgrade')
                install_command.extend(self.config.python.pip.install)
                logger.call(install_command)
            else:
                logger.warn('No pip packages to install')

