from __future__ import absolute_import
from dotfiles.package_base import *

@suggests('tmux_conf')
class tmux(PackageBase):
    def install(self):
        return self.action('apt-get').install(['tmux'])
