from __future__ import absolute_import
from dotfiles.package_base import *

class dircolors(PackageBase):
    def install(self):
        return self.action('file').symlink(self.home_file('.dircolors'), self.base_file('colors/LS_COLORS'))
