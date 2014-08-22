from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.src_package import *
from dotfiles.util import *

@suggests('gitg')
@suggests('gitconfig')
class git(PackageBase):
    def install(self):
        if self.config.local:
            package = SrcPackage(self, 'git', TarGzWebArchive('https://www.kernel.org/pub/software/scm/git/git-1.9.4.tar.gz'), 'git-1.9.4')
            return concat_lists(
                package.update(),
                package.configure(prefix=self.config.local_install.dir),
                package.make_install()
            )
        else:
            return self.action('apt-get').install(['git'])

