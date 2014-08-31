from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.src_package import *
from dotfiles.util import *

class htop(PackageBase):
    def install(self):
        if self.config.local:
            package = SrcPackage(self, 'htop', TarGzWebArchive('http://hisham.hm/htop/releases/1.0.3/htop-1.0.3.tar.gz', unique_file_url=True), 'htop-1.0.3')
            return concat_lists(
                package.update(),
                package.configure(prefix=self.config.local_install.dir),
                package.make(),
                package.make_install()
            )
        else:
            return self.action('apt-get').install(['htop'])
