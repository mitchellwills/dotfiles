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
    def do_config(self):
        def def_color(name, code):
            color_string = '\e['+code+'m'
            self.assign('bash_prompt_'+name, "'\["+color_string+"\]'")
            self.assign('bash_'+name, "'color_string'")

        for color in colors:
            def_color('normal', '0')
            def_color(color, '0;3'+colors[color])
            def_color('bold_'+color, "1;3"+colors[color])
            def_color('underline_'+color, "4;3"+colors[color])
            def_color('background_'+color, "4"+colors[color])

