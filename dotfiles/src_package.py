from __future__ import absolute_import
import dotfiles.logger as logger
import os
from dotfiles.actions import *
from dotfiles.package_base import *
from dotfiles.util import *

class SrcRepo(object):
    pass

class GitRepo(SrcRepo):
    def __init__(self, path, branch = None):
        self.path = path
        self.branch = branch
    def update(self, directory, context):
        result = []
        if os.path.isdir(directory):
            result.append(CommandAction(['git', 'fetch'], cwd=directory, deps=['git']))
        else:
            result.append(CommandAction(['git', 'clone', self.path, directory], deps=['git']))
        if self.branch is not None:
            result.append(CommandAction(['git', 'checkout', self.branch], cwd=directory, deps=['git']))
        return result

    def clean(self, directory, context):
        result = []
        result.append(CommandAction(['git', 'clean', '-xdf'], cwd=directory, deps=['git']))
        return result

class TarGzWebArchive(SrcRepo):
    def __init__(self, url):
        self.url = url
    def update(self, directory, context):
        targz_file = os.path.join(directory, os.path.basename(directory)+'.tar.gz')
        return concat_lists(
            context.action('file').mkdir(directory),
            context.action('net').wget(targz_file, self.url),
            context.action('archive').untar(targz_file, directory)
        )

    def clean(self, directory, context):
        return concat_lists(
            context.action('file').rmdir(directory),
        )


class SrcPackage(object):
    def __init__(self, context, name, src_repo, build_dir=None):
        self.context = context
        self.name = name
        self.src_repo = src_repo
        self.src_dir = self.context.src_file(self.name)
        if build_dir is None:
            self.build_dir = self.src_dir
        else:
            self.build_dir = os.path.join(self.src_dir, build_dir)

    def update(self):
        result = []
        if os.path.isdir(self.src_dir) and self.context.config.src.clean_src:
            result.extend(self.src_repo.clean(self.src_dir, self.context))
        result.extend(self.src_repo.update(self.src_dir, self.context))
        return result

    def configure(self, prefix = None, args=[]):
        configure_command = ['./configure']
        if prefix is not None:
            configure_command.append('--prefix='+os.path.expanduser(prefix))
        configure_command.extend(args)
        return [CommandAction(configure_command, cwd=self.build_dir)]

    def make_install(self, args=[], env=None):
        command = ['make', 'install']
        if self.context.config.src.make_args is not None:
            command.extend(self.context.config.src.make_args)
        command.extend(args)
        return [CommandAction(command, cwd=self.build_dir, env=env)]

class SrcPackageActionFactory(PackageActionFactory):
    def name(self):
        return 'src'

    def update(self, package):
        return package.update()

    def configure(self, package):
        return package.configure(prefix=self.config.local_install.dir)

    def make_install(self, package):
        return package.make_install()

    def update_configure_make_install(self, package):
        return concat_lists(self.update(package), self.configure(package), self.make_install(package))

@abstract
class SrcConfigureMakeInstallPackage(PackageBase):
    def __init__(self, pkg_name, repo):
        PackageBase.__init__(self)
        self.pkg_name = pkg_name
        self.repo = repo

    def name(self):
        return self.pkg_name

    def install(self):
        package = SrcPackage(self, self.pkg_name, self.repo)
        return self.action('src').update_configure_make_install(package)


