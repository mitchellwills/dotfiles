from __future__ import absolute_import
import os
from collections import OrderedDict
from install_util import *


class GitConfigEntry:
    def __init__(self, value, comment):
        self.value = value
        self.comment = comment

def init(obj):
    def add_config(name, value, comment = None):
        name_split = name.split('.')
        category = name_split[0]
        key = name_split[1]
        if not hasattr(obj, 'data'):
            obj.data = OrderedDict()
        if not category in obj.data:
            obj.data[category] = OrderedDict()
        obj.data[category][key] = GitConfigEntry(value, comment)
        
    obj.add_config = add_config

def config(obj, config):
    obj.add_config('user.name', config.identity.name)
    obj.add_config('user.email', config.identity.email)

    obj.add_config('color.branch', 'auto')
    obj.add_config('color.diff', 'auto')
    obj.add_config('color.interactive', 'auto')
    obj.add_config('color.status', 'auto')

    obj.add_config('push.default', 'simple')

def build(obj, builddir):
    if hasattr(obj, 'data'):
        with open(os.path.join(builddir, '.gitconfig'), 'w') as f:
            for category in obj.data:
                f.write('['+category+']\n')
                for key, entry in obj.data[category].iteritems():
                    if entry.comment:
                        f.write('\t# '+entry.comment+'\n')
                    f.write('\t'+key+' = '+entry.value+'\n')
                f.write('\n')

def install(obj, builddir):
    install_symlink_in_home('.gitconfig', os.path.join(builddir, '.gitconfig'))
