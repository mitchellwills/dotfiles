from __future__ import absolute_import
from module_base import *
from config_util import *

class BashrcAliases(ModuleBase):

    @before('Bashrc')
    def do_build(self):
        with open(self.build_file('gen/10-aliases.bash'), 'w') as f:
            for key in sorted(self.config.bash.aliases.keys()):
                value = self.config.bash.aliases[key]
                comment = self.config.bash.aliases[key+'.comment']
                if type(value) == Config:
                    name = value.name
                    value = value.value
                else:
                    name = key

                if comment is None:
                    f.write('alias '+name+'='+value+'\n')
                else:
                    f.write('alias '+name+'='+value+'\t\t# '+comment+'\n')

