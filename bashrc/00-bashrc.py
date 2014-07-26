from __future__ import absolute_import
import os
from build_util import *
from module_base import *


class Bashrc(ModuleBase):
    def do_init(self):
        os.mkdir(self.build_file('gen'))

    def all_files_recursive_with_basename(self, path):
        if not path.endswith('/'):
            path = path + '/'
        files = all_files_recursive(path)
        return map(lambda f: (f, f[len(path):]), files)
    def do_build(self):
        module_files = self.all_files_recursive_with_basename(self.module_file(''))
        gen_files = self.all_files_recursive_with_basename(self.build_file('gen'))

        files = map(lambda x: x[0], sorted(filter(lambda s: s[1].endswith('.bash'), module_files + gen_files), key=lambda x: x[1]))
        self.concatenate_files_to_build(files, '.bashrc')

    def do_install(self):
        self.symlink(self.home_file('.bashrc'), self.build_file('.bashrc'))
