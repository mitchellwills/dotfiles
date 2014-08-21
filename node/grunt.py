from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.util import *
import os

class grunt(PackageBase):
    def install(self):
        return self.action('npm').install(['grunt', 'grunt-cli'])
