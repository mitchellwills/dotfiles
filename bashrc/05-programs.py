from __future__ import absolute_import
from dotfiles.module_base import *

class BashrcPrograms(ModuleBase):

    @before('Bashrc')
    def do_build(self):
        with open(self.build_file('gen/05-programs.bash'), 'w') as f:
            f.write('export EDITOR='+self.config.bash.programs.editor+'\n')
            f.write('export PAGER='+self.config.bash.programs.pager+'\n')

