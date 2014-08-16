from __future__ import absolute_import
from dotfiles.package_base import *

@suggests('gitg')
@suggests('gitconfig')
class git(PackageBase):
    def install(self):
        return self.action('apt-get').install(['git'])

