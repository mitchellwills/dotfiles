from __future__ import absolute_import
from dotfiles.module_base import *
import os

class FluxGuiAptGet(ModuleBase):
    def do_config(self):
        if self.config.install and self.config.flux.install:
            self.config.apt_get.add('repos', ['ppa:kilian/f.lux'], 0)
            self.config.apt_get.add('install', ['fluxgui'], 0)

class Flux(ModuleBase):
    def do_install(self):
        if self.config.install and self.config.flux.install:
            self.download_build_file('xflux64.tgz', 'https://justgetflux.com/linux/xflux64.tgz')
            with logger.frame('Extracting xflux'):
                logger.call(['tar', '-xzf', self.build_file('xflux64.tgz'), '--directory='+self.build_file('')])
            with logger.frame('Installing xflux'):
                if self.config.sudo:
                    logger.call(['sudo', 'mv', self.build_file('xflux'), '/usr/bin'])
                else:
                    logger.call(['mv', self.build_file('xflux'), os.path.expanduser(self.config.local_install.dir)])
