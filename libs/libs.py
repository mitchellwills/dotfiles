from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.src_package import *

class libevent(PackageBase):
    def install(self):
        if self.config.local:
            package = SrcPackage(self, 'libevent', TarGzWebArchive('https://github.com/downloads/libevent/libevent/libevent-2.0.21-stable.tar.gz'), 'libevent-2.0.21-stable')
            return concat_lists(
                package.update(),
                package.configure(prefix=self.config.local_install.dir, args=['--disable-shared']),
                package.make_install()
            )
        else:
            return self.action('apt-get').install('libevent-dev')

class ncurses(PackageBase):
    def install(self):
        if self.config.local:
            package = SrcPackage(self, 'ncurses', TarGzWebArchive('ftp://ftp.gnu.org/gnu/ncurses/ncurses-5.9.tar.gz'), 'ncurses-5.9')
            return concat_lists(
                package.update(),
                package.configure(prefix=self.config.local_install.dir, args=['--disable-shared']),
                package.make_install()
            )
        else:
            return self.action('apt-get').install('libncurses5-dev')
