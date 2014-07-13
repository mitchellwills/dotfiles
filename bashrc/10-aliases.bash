#aliases
alias l='ls'
alias ll='ls -AlF'
alias lr='ll -R'           #  Recursive ls.
alias tree='tree -Csu'    #  Nice alternative to 'recursive ls' ...


alias ls='ls --color=always -h'
alias grep='grep --color=always'
alias fgrep='fgrep --color=always'
alias egrep='egrep --color=always'
alias mkdir='mkdir -p' #recursive directory make
alias less='less -R'

alias df='df -h'
alias du='du -h'

#make emacs only run in the terminal
alias emacs='emacs -nw'


alias rmtmp='rm -f *~;rm -f .*~'


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


alias ccc='ssh mwills@ccc.wpi.edu'
alias ccc1='ssh mwills@cccwork1.wpi.edu'
alias ccc2='ssh mwills@cccwork2.wpi.edu'
alias ccc3='ssh mwills@cccwork3.wpi.edu'
alias ccc4='ssh mwills@cccwork4.wpi.edu'

alias wpiwifi='nmcli con up id WPI-Wireless'
alias 3002wifi='nmcli con up id RBE_3002'


# git
alias g='git'
function git_pub() {
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo "Publishing ${BRANCH} to remote origin"
  git push -u origin $BRANCH
}
