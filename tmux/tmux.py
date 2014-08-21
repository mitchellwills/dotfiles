from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.src_package import *
from dotfiles.util import *
import os

@suggests('tmux_conf')
class tmux(PackageBase):
    def install(self):
        if self.config.local:
            package = SrcPackage(self, 'tmux', TarGzWebArchive('http://sourceforge.net/projects/tmux/files/tmux/tmux-1.9/tmux-1.9a.tar.gz/download'), 'tmux-1.9a')
            env = dict(os.environ)
            env['LDFLAGS'] = '-static'
            return concat_lists(
                [DependsAction(['libevent-dev', 'ncurses-dev'])],
                package.update(),
                package.configure(prefix=self.config.local_install.dir),
                package.make_install(env=env)
            )
        else:
            return self.action('apt-get').install(['tmux'])

