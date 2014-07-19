from __future__ import absolute_import
from module_base import *

colors = {
    'black':'0',
    'red':'1',
    'green':'2',
    'yellow':'3',
    'blue':'4',
    'purple':'5',
    'cyan':'6',
    'white':'7'
}

class BashrcPromptColors(ModuleBase):
    @before('Bashrc')
    def do_build(self):
        with open(self.build_file('gen/51-bash-colors.bash'), 'w') as f:
            def def_color(name, code):
                color_string = '\e['+code+'m'
                f.write("bash_prompt_"+name+"='\["+color_string+"\]'\n")
                f.write("bash_"+name+"='"+color_string+"'\n")

            def_color('normal', '0')
            for color in colors:
                def_color(color, '0;3'+colors[color])
                def_color('bold_'+color, "1;3"+colors[color])
                def_color('underline_'+color, "4;3"+colors[color])
                def_color('background_'+color, "4"+colors[color])

