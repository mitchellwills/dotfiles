from __future__ import absolute_import
from dotfiles.module_base import *

class BashrcPath(ModuleBase):

    def write_path_bash(self, f, paths, path_var):
        if len(paths) > 0:
            new_path = ''
            for path_entry in paths:
                new_path = new_path + path_entry+':'
            new_path = new_path + '$'+path_var
            f.write('export '+path_var+'='+new_path+'\n')

    @before('Bashrc')
    def do_build(self):
        with open(self.build_file('gen/91-path.bash'), 'w') as f:
            self.write_path_bash(f, self.config.bash.path, 'PATH')
            self.write_path_bash(f, self.config.bash.ldpath, 'LD_LIBRARY_PATH')

