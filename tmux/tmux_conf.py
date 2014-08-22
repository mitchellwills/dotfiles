from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.util import *

class TmuxConf(PackageBase):
    def name(self):
        return 'tmux_conf'

    def build_conf_file(self):
        commands = []

        def add_command(c, comment = None):
            if comment:
                commands.append(c+'  # '+comment)
            else:
                commands.append(c)

        set_option = lambda name, value, comment = None: add_command('set-option -g '+name+' '+value, comment)
        set_window_option = lambda name, value, comment = None: add_command('set-window-option -g '+name+' '+value, comment)

        unbind = lambda key, comment = None: add_command('unbind-key '+key, comment)
        bind = lambda key, command, comment = None: add_command('bind '+key+' '+command, comment)

        _ = lambda : add_command('')
        comment = lambda comment: add_command('# '+comment)

        comment('set prefix key')
        unbind('C-b')
        set_option('prefix', self.config.tmux.prefix)

        _()
        unbind('%', 'Remove default binding')
        bind('|', 'split-window -h')
        bind('_', 'split-window -v')

        _()
        set_option('status-bg', 'black')
        set_option('status-fg', 'white')

        _()
        set_option('base-index', '1')

        _()
        comment('Highlight active window')
        set_window_option('window-status-current-bg', 'red')

        _()
        set_window_option('monitor-activity', 'on')
        set_option('visual-activity', 'on')
        with open(self.build_file('.tmux.conf'), 'a') as f:
            for c in commands:
                f.write(c+'\n')

    def install(self):
        return concat_lists(
            [self.build_conf_file],
            self.action('file').symlink(self.home_file('.tmux.conf'), self.build_file('.tmux.conf'))
        )
