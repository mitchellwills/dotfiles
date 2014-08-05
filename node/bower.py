from __future__ import absolute_import
from dotfiles.package_base import *
import dotfiles.logger as logger

@depends('npm')
class bower(PackageBase):
    def install(self):
        return self.action('npm').install(['bower'])
