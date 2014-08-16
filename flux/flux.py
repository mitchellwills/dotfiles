from __future__ import absolute_import
from dotfiles.module_base import *
from dotfiles.package_base import *
import os

@depends('flux')
class fluxgui(PackageBase):
    def install(self):
        return concat_lists(
            self.action('apt-get').add_repo('ppa:kilian/f.lux'),
            self.action('apt-get').update(),
            self.action('apt-get').install(['fluxgui'])
        )

@suggests('fluxgui')
class flux(PackageBase):
    def install(self):
        actions = concat_lists(
            self.action('net').download(self.build_file('xflux64.tgz'), 'https://justgetflux.com/linux/xflux64.tgz'),
            self.action('archive').untar(self.build_file('xflux64.tgz'), self.build_file('')),
        )

        if self.config.local:
            actions.extend(self.action('file').mv(self.build_file('xflux'), os.path.join(os.path.expanduser(self.config.local_install.dir), 'bin')))
        else:
            actions.extend(self.action('file').mv(self.build_file('xflux'), '/usr/bin', sudo=True))

        return actions
