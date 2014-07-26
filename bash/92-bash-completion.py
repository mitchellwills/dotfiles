from __future__ import absolute_import
from dotfiles.module_base import *
import os

class BashrcCompletion(ModuleBase):
    @before('Bashrc')
    def do_build(self):
        with open(self.build_file('gen/92-bash-completion.bash'), 'w') as f:
            for completion_dir in self.config.bash.completion_dir:
                f.write('for f in '+os.path.join(completion_dir, '*')+'; do\n')
                f.write('\tsource $f\n')
                f.write('done\n')
            for completion_file in self.config.bash.completion_file:
                f.write('if [ -f '+completion_file+' ]; then\n')
                f.write('\tsource '+completion_file+'\n')
                f.write('fi\n')

