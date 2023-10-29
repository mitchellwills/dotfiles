alias emacs='emacs -nw'         # make emacs only run in the terminal

# Directory aliases
alias -- -='cd -'               # go to the previous directory
alias -g ...='../..'
alias -g ....='../../..'
alias -g .....='../../../..'
alias -g ......='../../../../..'

alias l='ls'
alias less='less -R'
alias ll='l -Al'
alias lll='ll -a'
alias llll='lll -i'
alias lr='ll -R'                # Recursive ls

if [[ $osname == 'Darwin' ]]; then
    alias ls='ls -h -F -G'
else
    alias ls='ls -h -F --color=auto'
fi

alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'

alias df='df -h'
alias du='du -h'
alias grep-rec='find . -type f -print0 | xargs -0 grep'

alias mkdir='mkdir -p'          # recursive directory make
alias rmtmp='rm -f *~;rm -f .*~'                # delete all file ending in ~ in the current directory
alias tree='tree -aChsu'                # Nice alternative to recursive ls
alias webserver='python3 -m http.server'            # Simple web server
alias what=which
alias when=date
alias where=which
alias which='type -a'


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



if [[ -z $TMUX ]]; then
    local tmux_session_lines
    tmux_session_lines=("${(@f)$(tmux list-sessions 2> /dev/null)}")

    if [[ $tmux_session_lines[1] == '' ]]; then
        echo "No active tmux sessions"
    else
        echo "Active tmux sessions:"
        for line in $tmux_session_lines; do
            print $line
        done
    fi
fi

function tmux-copy() { tmux save-buffer - | DISPLAY=:0 xclip -selection clipboard }
alias tmc=tmux-copy
