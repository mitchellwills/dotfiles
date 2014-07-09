from __future__ import absolute_import
from module_base import *

class BashPath:
    def __init__(self, var):
        self.path_entries = []
        self.var = var
    def build(self):
        if len(self.path_entries) > 0:
            new_path = ''
            for path_entry in self.path_entries:
                new_path = new_path + path_entry+':'
            new_path = new_path + '$'+self.var
            return 'export '+self.var+'='+new_path
        return ''

class BashrcPath(ModuleBase):
    def do_init(self):
        bash_path = BashPath('PATH')
        bash_ldpath = BashPath('LD_LIBRARY_PATH')
        self.def_common('bash_path', bash_path)
        self.def_common('bash_ldpath', bash_ldpath)
        self.def_common('add_path', lambda path_entry: self.bash_path.path_entries.append(path_entry))
        self.def_common('add_ldpath', lambda path_entry: self.bash_ldpath.path_entries.append(path_entry))

    def do_config(self):
        self.add_command(self.bash_path)
        self.add_command(self.bash_ldpath)

        for path in self.config.bash.path:
            self.add_path(path)

        for path in self.config.bash.ldpath:
            self.add_ldpath(path)

