# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"


function myps() { ps $@ -u $USER -o pid,%cpu,%mem,bsdtime,command ; }
function pstree() { myps f | awk '!/awk/ && $0~var' var=${1:-".*"} ; }


if [ -f ~/.local.bashrc ]; then
    source ~/.local.bashrc
fi


