from __future__ import absolute_import
import os
from build_util import *
from install_util import *


def init(obj):
    obj.commands = []
    def add_command(c, comment = None):
        if comment:
            obj.commands.append(c+' # '+comment)
        else:
            obj.commands.append(c)

    obj.add_command = add_command

    obj.set_option = lambda name, value, comment = None: obj.add_command('set-option -g '+name+' '+value, comment)
    obj.set_window_option = lambda name, value, comment = None: obj.add_command('set-window-option -g '+name+' '+value, comment)

    obj.unbind = lambda key, comment = None: obj.add_command('unbind-key '+key, comment)
    obj.bind = lambda key, command, comment = None: obj.add_command('bind '+key+' '+command, comment)

    obj._ = lambda : obj.add_command('')
    obj.comment = lambda comment: obj.add_command('# '+comment)

def config(obj, config):
    obj.comment('set prefix key')
    obj.unbind('C-b')
    obj.set_option('prefix', config.tmux.prefix)

    obj._()
    obj.unbind('%', 'Remove default binding')
    obj.bind('|', 'split-window -h')
    obj.bind('_', 'split-window -v')

    obj._()
    obj.set_option('status-bg', 'black')
    obj.set_option('status-fg', 'white')

    obj._()
    obj.comment('Highlight active window')
    obj.set_window_option('window-status-current-bg', 'red')

    obj._()
    obj.set_window_option('monitor-activity', 'on')
    obj.set_option('visual_activity', 'on')

def build(obj, builddir):
    with open(os.path.join(builddir, '.tmux.conf'), 'w') as f:
        for c in obj.commands:
            f.write(c+'\n')

def install(obj, builddir):
    install_symlink_in_home('.tmux.conf', os.path.join(builddir, '.tmux.conf'))
