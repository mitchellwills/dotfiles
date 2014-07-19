from __future__ import absolute_import
from module_base import *
from config_util import *
from build_util import *

colors = [
    'black',
    'red',
    'green',
    'yellow',
    'blue',
    'purple',
    'cyan',
    'white'
]
color_prefixes = [
    '',
    'background_',
    'bold_',
    'underline_',
]

def expand(text):
    for color in colors:
        for prefix in color_prefixes:
            text = text.replace('%'+prefix+color, '${bash_prompt_'+prefix+color+'}')
    text = text.replace('%normal', '${bash_prompt_normal}')
    return text

class BashrcPrompt(ModuleBase):
    @before('Bashrc')
    def do_build(self):
        with open(self.build_file('gen/85-prompt.bash'), 'w') as f:
            files = filter(lambda f: f.endswith('.promptbash'), all_files_recursive(self.module_file('')))
            for prompt_f in files:
                f.write(open(prompt_f, 'r').read())
                f.write('\n')

            f.write('function prompt_command() {\n')
            f.write('\tEXIT_STATUS=$?\n')
            for statement in self.config.bash.prompt['eval']:
                f.write('\t'+statement+'\n')
            for var in self.config.bash.prompt.vars.keys():
                value = self.config.bash.prompt.vars[var]
                if type(value) is Config:
                    f.write('\tif [ '+value['if']+' ]; then\n')
                    f.write('\t\t'+var+'='+expand(value['then'])+'\n')
                    f.write('\telse\n')
                    f.write('\t\t'+var+'='+expand(value['else'])+'\n')
                    f.write('\tfi\n')
                else:
                    f.write('\t'+var+'='+expand(value)+'\n')
            f.write('\tPS1='+expand(self.config.bash.prompt.template)+'\n')

            f.write('\t# set title bar\n')
            f.write('\tcase "$TERM" in\n')
            f.write('\t\txterm*|rxvt*)\n')
            f.write('\t\t\tPS1="\\[\\e]0;\\u@\\h: \\w\\a\\]$PS1"\n')
            f.write('\t\t\t;;\n')
            f.write('\t\t*)\n')
            f.write('\t\t\t;;\n')
            f.write('\tesac\n')
            f.write('\t\n')
            f.write('}\n')
            f.write('PROMPT_COMMAND=prompt_command;')
