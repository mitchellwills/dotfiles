export PS1="\[\e[00;33m\]\u\[\e[0m\]\[\e[00;37m\]@\h:\[\e[0m\]\[\e[00;36m\][\w]:\[\e[0m\]\[\e[00;37m\] \[\e[0m\]"
export EDITOR=emacs

#shell options
shopt -s cdspell
shopt -s cmdhist
shopt -s extglob

#aliases
alias ll='ls -alF'
alias lr='ll -R'           #  Recursive ls.
alias tree='tree -Csu'    #  Nice alternative to 'recursive ls' ...

alias rmtmp='rm -f *~;rm -f .*~'


alias mkdir='mkdir -p' #recursive directory make

alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias -- -='cd -'

# Add colors for filetype and  human-readable sizes by default on 'ls':
alias ls='ls -h --color'


export PAGER=less

# Adds some text in the terminal frame (if applicable).
function xtitle()
{
    case "$TERM" in
    *term* | rxvt)
        echo -en  "\e]0;$*\a" ;;
    *)  ;;
    esac
}

function extract()      # Handy Extract Program
{
    if [ -f $1 ] ; then
        case $1 in
            *.tar.bz2)   tar xvjf $1     ;;
            *.tar.gz)    tar xvzf $1     ;;
            *.bz2)       bunzip2 $1      ;;
            *.rar)       unrar x $1      ;;
            *.gz)        gunzip $1       ;;
            *.tar)       tar xvf $1      ;;
            *.tbz2)      tar xvjf $1     ;;
            *.tgz)       tar xvzf $1     ;;
            *.zip)       unzip $1        ;;
            *.Z)         uncompress $1   ;;
            *.7z)        7z x $1         ;;
            *)           echo "'$1' cannot be extracted via >extract<" ;;
        esac
    else
        echo "'$1' is not a valid file!"
    fi
}

# Creates an archive (*.tar.gz) from given directory.
function maketar() { tar cvzf "${1%%/}.tar.gz"  "${1%%/}/"; }

# Create a ZIP archive of a file or folder.
function makezip() { zip -r "${1%%/}.zip" "$1" ; }

function myps() { ps $@ -u $USER -o pid,%cpu,%mem,bsdtime,command ; }
function pstree() { my_ps f | awk '!/awk/ && $0~var' var=${1:-".*"} ; }

if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi
