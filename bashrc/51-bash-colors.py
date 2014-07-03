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
        for color in colors:
            self.assign('normal', "'\[\e[0m\]'")
            self.assign(color, "'\[\e[0;3"+colors[color]+"m\]'")
            self.assign('bold_'+color, "'\[\e[1;3"+colors[color]+"m\]'")
            self.assign('underline_'+color, "'\[\e[4;3"+colors[color]+"m\]'")
            self.assign('background_'+color, "'\[\e[4"+colors[color]+"m\]'")
