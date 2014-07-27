from __future__ import absolute_import
from dotfiles.module_base import *
from dotfiles.src_package import *
import dotfiles.logger as logger


class PipInstall(ModuleBase):
    def do_config(self):
        self.config.apt_get.add('install', ['python-pip'], 0)
    @after('AptGetInstall')
    def do_install(self):
        if self.config.install:
            if self.config.python.pip.install:
                install_command = ['sudo', 'pip', 'install']
                if self.config.upgrade:
                    install_command.append('--upgrade')
                install_command.extend(self.config.python.pip.install)
                logger.call(install_command)
            else:
                logger.warn('No pip packages to install')

