from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.src_package import *
from dotfiles.util import *

class libevent(PackageBase):
    def name(self):
        return 'libevent-dev'
    def install(self):
        if self.config.local:
            package = SrcPackage(self, 'libevent', TarGzWebArchive('https://github.com/downloads/libevent/libevent/libevent-2.0.21-stable.tar.gz', unique_file_url=True), 'libevent-2.0.21-stable')
            return concat_lists(
                package.update(),
                package.configure(prefix=self.config.local_install.dir, args=['--disable-shared']),
                package.make_install()
            )
        else:
            return self.action('apt-get').install('libevent-dev')

class ncurses(PackageBase):
    def name(self):
        return 'ncurses-dev'
    def install(self):
        if self.config.local:
            package = SrcPackage(self, 'ncurses', TarGzWebArchive('ftp://ftp.gnu.org/gnu/ncurses/ncurses-5.9.tar.gz', unique_file_url=True), 'ncurses-5.9')
            return concat_lists(
                package.update(),
                package.configure(prefix=self.config.local_install.dir, args=['--disable-shared']),
                package.make_install()
            )
        else:
            return self.action('apt-get').install('libncurses5-dev')
