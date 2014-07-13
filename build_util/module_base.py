from __future__ import print_function
import os
import re
from install_util import *
import inspect
import functools
import urllib2
import logger

class ModuleContext(object):
    def __init__(self, wd, builddir, config, common):
        self.wd = wd
        self.builddir = builddir
        self.config = config
        self.common = common

    def build_file(self, name):
        return os.path.join(self.builddir, name)

    def module_file(self, name):
        return os.path.join(self.wd, name)

    def home_file(self, name):
        return os.path.expanduser(os.path.join('~/', name))

    def amend_build_file(self, name, amendment):
        with open(self.build_file(name), 'a') as f:
            f.write(amendment)
    def amend_build_file_with_file(self, name, other_file):
        with open(other_file, 'r') as f:
            self.amend_build_file(name, f.read())

    def concatenate_files_to_build(self, files, build_file):
        for f in files:
            with logger.trylog('amending ' + f + ' -> ' + build_file):
                self.amend_build_file_with_file(build_file, f)

    def download_build_file(self, name, url):
        with logger.trylog('downloading ' + url + ' -> ' + name):
            response = urllib2.urlopen(url)
            contents = response.read()
            with open(self.build_file(name), 'w') as f:
                f.write(contents)


class ModuleCommon:
    def __init__(self):
        self.properties = dict()


class ModuleBase(object):
    def __init__(self, context):
        self.context = context
        self.config = context.config

    def __getattr__(self, name):
        if name in ModuleContext.__dict__:
            return lambda *args, **kwargs: ModuleContext.__dict__[name](self.context, *args, **kwargs)
        return self.context.common.properties[name]

    def def_common(self, name, value):
        if name in self.context.common.properties:
            raise Exception('Redefinition of ', name)
        self.context.common.properties[name] = value

def before(spec):
    def wrap(func):
        if not hasattr(func, 'before'):
            func.before = set()
        func.before.add(spec)
        return func
    return wrap
def after(spec):
    def wrap(func):
        if not hasattr(func, 'after'):
            func.after = set()
        func.after.add(spec)
        return func
    return wrap
