

#aliases
alias l='ls'
alias ll='ls -AlF'
alias lr='ll -R'           #  Recursive ls.
alias tree='tree -Csu'    #  Nice alternative to 'recursive ls' ...

alias rmtmp='rm -f *~;rm -f .*~'

alias mkdir='mkdir -p' #recursive directory make

alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias -- -='cd -'
alias ~='cd'

#alias which='alias | /usr/bin/which --tty-only --read-alias --show-dot --show-tilde'
alias which='type -a'
alias where=which
alias what=which
alias when=date

alias e=$EDITOR

# Add colors for filetype and  human-readable sizes by default on 'ls':
alias ls='ls -h --color'


alias ccc='ssh mwills@ccc.wpi.edu'

alias wpiwifi='nmcli con up id WPI-Wireless'
alias 3002wifi='nmcli con up id RBE_3002'

