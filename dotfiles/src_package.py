from __future__ import absolute_import
import dotfiles.logger as logger
import os
from dotfiles.actions import *
from dotfiles.package_base import *
from dotfiles.util import *

__all__ = ['SrcRepo', 'GitRepo', 'TarGzWebArchive', 'SrcPackage', 'SrcPackageActionFactory', 'SrcConfigureMakeInstallPackage']

class SrcRepo(object):
    pass

class GitRepo(SrcRepo):
    def __init__(self, path, branch = None):
        self.path = path
        self.branch = branch
    def update(self, directory, context, package):
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
    def __init__(self, url, unique_file_url=False):
        self.url = url
        self.unique_file_url = unique_file_url
    def update(self, directory, context, package):
        targz_file = os.path.join(directory, os.path.basename(directory)+'.tar.gz')
        download_url_file = os.path.join(directory, 'last_download')
        def check_download_up_to_date():
            if self.unique_file_url and os.path.isfile(download_url_file):
                with open(download_url_file, 'r') as f:
                    if f.read() == self.url:
                        logger.warning('Detected that source url has not changed')
                        return False
            return True
        def write_download_url():
            with open(download_url_file, 'w') as f:
                f.write(self.url)
        def assign_package_modified(matches):
            package.modified = not matches
            if not package.modified:
                logger.warning('Detected that source has not changed (tar MD5)')
        return concat_lists(
            context.action('file').mkdir(directory),
            context.action('lazy').ifthen(check_download_up_to_date, concat_lists(
                    context.action('net').wget(targz_file, self.url),
                    [write_download_url]
                    )),
            context.action('md5').check(targz_file, assign_package_modified),
            context.action('lazy').ifthen(lambda: package.modified, concat_lists(
                    context.action('md5').compute_to_file(targz_file),
                    context.action('archive').untar(targz_file, directory)
                    ))
        )

    def clean(self, directory, context):
        return concat_lists(
            context.action('file').rmdir(directory, force=True),
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
        self.modified = True

    def update(self):
        result = []
        if os.path.isdir(self.src_dir) and self.context.config.src.clean_src:
            result.extend(self.src_repo.clean(self.src_dir, self.context))
        result.extend(self.src_repo.update(self.src_dir, self.context, self))
        return result

    def run_lazy(self, actions, warning_message, lazy=True):
        if lazy:
            return self.context.action('lazy').ifthenelse(lambda: self.modified, actions,
                                                          [lambda: logger.warning(warning_message)])
        return actions

    def run_command_lazy(self, command, lazy=True, **kwargs):
        actions = [CommandAction(command, **kwargs)]
        return self.run_lazy(actions, 'Not running: '+str(command))

    def configure(self, prefix = None, args=[], lazy=True):
        configure_command = ['./configure']
        if prefix is not None:
            configure_command.append('--prefix='+os.path.expanduser(prefix))
        configure_command.extend(args)
        return self.run_command_lazy(configure_command, lazy=lazy, cwd=self.build_dir)

    def make(self, args=[], env=None, lazy=True):
        command = ['make']
        command.extend(args)
        if self.context.config.src.make_args is not None:
            command.extend(self.context.config.src.make_args)
        return self.run_command_lazy(command, lazy=lazy, cwd=self.build_dir, env=env)

    def make_install(self, args=[], env=None, lazy=True):
        new_args = ['install']
        new_args.extend(args)
        return self.make(args=new_args, env=env, lazy=lazy)

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


