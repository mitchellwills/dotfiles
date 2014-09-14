from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.src_package import *
from dotfiles.util import *

@suggests('emacs:racket-mode')
class racket(PackageBase):
    def install(self):
        if self.config.local:
            package = SrcPackage(self, 'racket', TarGzWebArchive('http://mirror.racket-lang.org/installers/6.1/racket-6.1-src-builtpkgs.tgz', unique_file_url=True), 'racket-6.1/src')
            return concat_lists(
                package.update(),
                package.configure(prefix=self.config.local_install.dir),
                package.make(),
                package.make(['plain-install'])
            )
        else:
            return self.action('apt-get').install(['racket'])
