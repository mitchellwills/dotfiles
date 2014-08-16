from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.src_package import *

@suggests('npm')
class NodePackage(SrcConfigureMakeInstallPackage):
    def __init__(self):
        SrcConfigureMakeInstallPackage.__init__(self, 'node', GitRepo('https://github.com/joyent/node.git', 'v0.11.13'))
