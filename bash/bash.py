from __future__ import absolute_import
from dotfiles.package_base import *

@suggests('bashrc')
class bash(PackageBase):
    def install(self):
        return self.action('apt-get').install(['bash'])

