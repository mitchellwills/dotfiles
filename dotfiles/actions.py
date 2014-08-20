from __future__ import absolute_import
import os
import dotfiles.logger as logger
import urllib2
from dotfiles.package_base import *

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

class CommandAction(object):
    def __init__(self, command, deps = None):
        self.command = command
        if deps is not None:
            for dep in deps:
                depends(dep)(self)

    def __call__(self):
        logger.call(self.command)

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

class ArchivePackageActionFactory(PackageActionFactory):
    def name(self):
        return 'archive'

    def untar(self, archive, dest):
        return [CommandAction(['tar', '-xzf', archive, '--directory='+dest])]

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
