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

def config(obj, config):
    for color in colors:
        obj.assign('normal', "'\[\e[0m\]'")
        obj.assign(color, "'\[\e[0;3"+colors[color]+"m\]'")
        obj.assign('bold_'+color, "'\[\e[1;3"+colors[color]+"m\]'")
        obj.assign('underline_'+color, "'\[\e[4;3"+colors[color]+"m\]'")
        obj.assign('background_'+color, "'\[\e[4"+colors[color]+"m\]'")
