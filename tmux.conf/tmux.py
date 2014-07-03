from __future__ import absolute_import
import os
from build_util import *
from install_util import *
from module_base import *


class Tmux(ModuleBase):
    def do_init(self):
        commands = []
        self.def_common('commands', commands)

        def add_command(c, comment = None):
            if comment:
                self.commands.append(c+' # '+comment)
            else:
                self.commands.append(c)

        self.def_common('add_command', add_command)

        self.def_common('set_option', lambda name, value, comment = None: self.add_command('set-option -g '+name+' '+value, comment))
        self.def_common('set_window_option', lambda name, value, comment = None: self.add_command('set-window-option -g '+name+' '+value, comment))

        self.def_common('unbind', lambda key, comment = None: self.add_command('unbind-key '+key, comment))
        self.def_common('bind', lambda key, command, comment = None: self.add_command('bind '+key+' '+command, comment))

        self.def_common('_', lambda : self.add_command(''))
        self.def_common('comment', lambda comment: self.add_command('# '+comment))

    def do_config(self):
        self.comment('set prefix key')
        self.unbind('C-b')
        self.set_option('prefix', self.config.tmux.prefix)

        self._()
        self.unbind('%', 'Remove default binding')
        self.bind('|', 'split-window -h')
        self.bind('_', 'split-window -v')

        self._()
        self.set_option('status-bg', 'black')
        self.set_option('status-fg', 'white')

        self._()
        self.set_option('base-index', '1')

        self._()
        self.comment('Highlight active window')
        self.set_window_option('window-status-current-bg', 'red')

        self._()
        self.set_window_option('monitor-activity', 'on')
        self.set_option('visual-activity', 'on')

    def do_build(self):
        with open(self.build_file('.tmux.conf'), 'a') as f:
            for c in self.commands:
                f.write(c+'\n')

    def do_install(self):
        install_symlink_in_home('.tmux.conf', self.build_file('.tmux.conf'))
