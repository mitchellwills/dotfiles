from __future__ import absolute_import
import os
import dotfiles.logger as logger
import urllib2
from dotfiles.package_base import *
from dotfiles.util import *

__all__ = ['PackageActionFactory', 'DependsAction', 'CommandAction', 'DownloadAction', 'SystemActionFactory', 'NetPackageActionFactory', 'ArchivePackageActionFactory', 'FilePackageActionFactory', 'SymlinkAction']

@abstract
class PackageActionFactory(object):
    def __init__(self):
        self.context = None

    def init_factory(self, context):
        self.context = context

    def __getattr__(self, name):
        if self.context is None:
            raise Exception('Action Factory not yet initialized')
        return getattr(self.context, name)

class DependsAction(object):
    def __init__(self, deps):
        for dep in deps:
            depends(dep)(self)

    def __call__(self):
        pass

class LazyAction(object):
    def __init__(self, action_generator):
        self.action_generator = action_generator
    def __call__(self):
        actions = self.action_generator()
        for action in actions:
            action()

class CommandAction(object):
    def __init__(self, command, deps = None, **kwargs):
        self.command = command
        self.kwargs = kwargs
        if deps is not None:
            for dep in deps:
                depends(dep)(self)

    def __call__(self):
        logger.call(self.command, **self.kwargs)

class DownloadAction(object):
    def __init__(self, dest, url):
        self.dest = dest
        self.url = url

    def __call__(self):
        with logger.trylog('downloading ' + self.url + ' -> ' + self.dest):
            response = urllib2.urlopen(self.url)
            contents = response.read()
            with open(self.dest, 'w') as f:
                f.write(contents)


class SystemActionFactory(PackageActionFactory):
    def name(self):
        return 'system'

    def command(self, command):
        return [CommandAction(command)]

class NetPackageActionFactory(PackageActionFactory):
    def name(self):
        return 'net'

    def download(self, dest, url):
        return [DownloadAction(dest, url)]

    def wget(self, dest, url):
        return [CommandAction(['wget', '--no-check-certificate', '-O', dest, url])]

class ArchivePackageActionFactory(PackageActionFactory):
    def name(self):
        return 'archive'

    def untar(self, archive, dest):
        return [CommandAction(['tar', '-xzf', archive, '--directory='+dest])]

class Md5ActionFactory(PackageActionFactory):
    def name(self):
        return 'md5'

    def compute_to_file(self, filename):
        def write_to_file():
            with open(filename+'.md5', 'w') as md5_file:
                logger.call(['md5sum', '-b', filename], stdout=md5_file)
        return [write_to_file]

    def check(self, filename, action):
        def func():
            result = subprocess.call(['md5sum', '-c', filename+'.md5'])
            action(True if result == 0 else False)
        return [func]

class LazyActionFactory(PackageActionFactory):
    def name(self):
        return 'lazy'

    def ifthenelse(self, condition, then_actions, else_actions):
        return [LazyAction(lambda: then_actions if condition() else else_actions)]

    def ifthen(self, condition, actions):
        return self.ifthenelse(condition, actions, [])

class FilePackageActionFactory(PackageActionFactory):
    def name(self):
        return 'file'

    def mv(self, src, dest, sudo=False):
        if sudo:
            return [CommandAction(['sudo', 'mv', src, dest])]
        else:
            return [CommandAction(['mv', src, dest])]

    def mkdir(self, d):
        return [CommandAction(['mkdir', '-p', d])]

    def rmdir(self, d, force=False):
        if force:
            return [CommandAction(['rm', '-rf', d])]
        else:
            return [CommandAction(['rm', '-r', d])]

    def symlink(self, name, target_path):
        return [SymlinkAction(name, target_path)]

class SymlinkAction(object):
    def __init__(self, name, target_path):
        self.name = name
        self.target_path = target_path

    def __call__(self):
        if os.path.lexists(self.name):
            if os.path.realpath(self.name) == self.target_path:
                logger.warning('symlink already exists ('+self.name+' -> '+self.target_path+')')
            else:
                with logger.trylog('backing up old file and createing symlink ('+self.name+' -> '+self.target_path+')'):
                    os.rename(self.name, self.name+'.bak');
                    os.symlink(self.target_path, self.name)
        else:
            with logger.trylog('createing symlink ('+self.name+' -> '+self.target_path+')'):
                os.symlink(self.target_path, self.name)
