from __future__ import absolute_import
from module_base import *
import os

class BashrcCompletion(ModuleBase):
    @before('Bashrc')
    def do_build(self):
        with open(self.build_file('gen/92-bash-completion.bash'), 'w') as f:
            for completion_dir in self.config.bash.completion:
               f.write('for f in '+os.path.join(completion_dir, '*')+'; do source $f; done')

