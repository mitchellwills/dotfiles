##01-head.bashrc
# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac


##02-shellopt.bashrc
# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

#correct minor errors in directory spelling
shopt -s cdspell

#use extended pattern matching features
shopt -s extglob

# don't put duplicate lines or lines starting with space in the history.
HISTCONTROL=ignorespace:ignoredups
# append to the history file, don't overwrite it
shopt -s histappend
# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000
HISTIGNORE='l:ll:lll:llll:ls:exit'


#disable flow control ^S and ^Q
stty -ixon

##03-symbols.bashrc
DOWN_ARROW_SYMBOL=$'\xe2\x86\x93'
RIGHT_ARROW_SYMBOL=$'\xe2\x86\x92'
UP_ARROW_SYMBOL=$'\xe2\x86\x91'
LEFT_ARROW_SYMBOL=$'\xe2\x86\x90'
PLUS_MINUS_SYMBOL=$'±'
X_SYMBOL="✗"
CHECK_SYMBOL="✓"

##05-programs
export EDITOR='emacs -nw'
export PAGER=less

##10-aliases
alias -- -='cd -' # go to the previous directory
alias ~='cd'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias df='df -h'
alias du='du -h'
alias egrep='egrep --color=always'
alias emacs='emacs -nw' # make emacs only run in the terminal
alias fgrep='fgrep --color=always'
alias grep='grep --color=always'
alias grep-rec='find . -type f -print0 | xargs -0 grep'
alias killbg='kill $(jobs -p)' # kill all background tasks
alias l='ls -F'
alias less='less -R'
alias ll='l -Al'
alias lll='ll -a'
alias llll='lll -i'
alias lr='ll -R' # Recursive ls
alias ls='ls --color=always -h'
alias mkdir='mkdir -p' # recursive directory make
alias rmtmp='rm -f *~;rm -f .*~' # delete all file ending in ~ in the current directory
alias tree='tree -aChsu' # Nice alternative to recursive ls
alias webserver='python3 -m http.server' # Simple web server

##50-colors.bashrc

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
fi

##51-bash-colors
bash_prompt_normal='\[\e[0m\]'
bash_normal='\e[0m'
bash_prompt_blue='\[\e[0;34m\]'
bash_blue='\e[0;34m'
bash_prompt_bold_blue='\[\e[1;34m\]'
bash_bold_blue='\e[1;34m'
bash_prompt_underline_blue='\[\e[4;34m\]'
bash_underline_blue='\e[4;34m'
bash_prompt_background_blue='\[\e[44m\]'
bash_background_blue='\e[44m'
bash_prompt_black='\[\e[0;30m\]'
bash_black='\e[0;30m'
bash_prompt_bold_black='\[\e[1;30m\]'
bash_bold_black='\e[1;30m'
bash_prompt_underline_black='\[\e[4;30m\]'
bash_underline_black='\e[4;30m'
bash_prompt_background_black='\[\e[40m\]'
bash_background_black='\e[40m'
bash_prompt_yellow='\[\e[0;33m\]'
bash_yellow='\e[0;33m'
bash_prompt_bold_yellow='\[\e[1;33m\]'
bash_bold_yellow='\e[1;33m'
bash_prompt_underline_yellow='\[\e[4;33m\]'
bash_underline_yellow='\e[4;33m'
bash_prompt_background_yellow='\[\e[43m\]'
bash_background_yellow='\e[43m'
bash_prompt_cyan='\[\e[0;36m\]'
bash_cyan='\e[0;36m'
bash_prompt_bold_cyan='\[\e[1;36m\]'
bash_bold_cyan='\e[1;36m'
bash_prompt_underline_cyan='\[\e[4;36m\]'
bash_underline_cyan='\e[4;36m'
bash_prompt_background_cyan='\[\e[46m\]'
bash_background_cyan='\e[46m'
bash_prompt_purple='\[\e[0;35m\]'
bash_purple='\e[0;35m'
bash_prompt_bold_purple='\[\e[1;35m\]'
bash_bold_purple='\e[1;35m'
bash_prompt_underline_purple='\[\e[4;35m\]'
bash_underline_purple='\e[4;35m'
bash_prompt_background_purple='\[\e[45m\]'
bash_background_purple='\e[45m'
bash_prompt_green='\[\e[0;32m\]'
bash_green='\e[0;32m'
bash_prompt_bold_green='\[\e[1;32m\]'
bash_bold_green='\e[1;32m'
bash_prompt_underline_green='\[\e[4;32m\]'
bash_underline_green='\e[4;32m'
bash_prompt_background_green='\[\e[42m\]'
bash_background_green='\e[42m'
bash_prompt_white='\[\e[0;37m\]'
bash_white='\e[0;37m'
bash_prompt_bold_white='\[\e[1;37m\]'
bash_bold_white='\e[1;37m'
bash_prompt_underline_white='\[\e[4;37m\]'
bash_underline_white='\e[4;37m'
bash_prompt_background_white='\[\e[47m\]'
bash_background_white='\e[47m'
bash_prompt_red='\[\e[0;31m\]'
bash_red='\e[0;31m'
bash_prompt_bold_red='\[\e[1;31m\]'
bash_bold_red='\e[1;31m'
bash_prompt_underline_red='\[\e[4;31m\]'
bash_underline_red='\e[4;31m'
bash_prompt_background_red='\[\e[41m\]'
bash_background_red='\e[41m'

##70-status.bashrc
s()
{
  pwd;
  echo
  l;
  if which git &> /dev/null && [[ -n "$(git rev-parse HEAD 2> /dev/null)" ]]; then
    echo
    git st;
  fi

}

##85-prompt
SCM_SYMBOL=$PLUS_MINUS_SYMBOL
SCM_DIRTY_SYMBOL="${bash_prompt_red}$X_SYMBOL"
SCM_CLEAN_SYMBOL="${bash_prompt_green}$CHECK_SYMBOL"

function git_prompt_vars {
  local status="$(git status -bs --porcelain 2> /dev/null)"
  local status_first_line="$(head -n1 <<< "${status}")"

  local ref=$(git symbolic-ref HEAD 2> /dev/null)
  SCM_BRANCH=${ref#refs/heads/}
  SCM_CHANGE=$(git rev-parse --short HEAD 2>/dev/null)

  SCM_GIT_AHEAD=''
  SCM_GIT_BEHIND=''
  local ahead_re='.+ahead ([0-9]+).+'
  local behind_re='.+behind ([0-9]+).+'
  [[ "${status_first_line}" =~ ${ahead_re} ]] && SCM_GIT_AHEAD="${BASH_REMATCH[1]}"
  [[ "${status_first_line}" =~ ${behind_re} ]] && SCM_GIT_BEHIND="${BASH_REMATCH[1]}"

  SCM_GIT_UPSTREAM_REMOTE=''
  SCM_GIT_UPSTREAM_BRANCH=''
  local upstream_re='.+\.\.\.([[:print:]]+)/([^[:space:]]+)'
  [[ "${status_first_line}" =~ ${upstream_re} ]] && SCM_GIT_UPSTREAM_REMOTE="${BASH_REMATCH[1]}" && SCM_GIT_UPSTREAM_BRANCH="${BASH_REMATCH[2]}"

  SCM_GIT_STASH_COUNT="$(git stash list 2> /dev/null | wc -l | tr -d ' ')"
  SCM_GIT_STAGED_COUNT="$(tail -n +2 <<< "${status}" | grep -v ^[[:space:]?]  | wc -l | tr -d ' ')"
  SCM_GIT_UNSTAGED_COUNT="$(tail -n +2 <<< "${status}" | grep ^.[^[:space:]?]  | wc -l | tr -d ' ')"
  SCM_GIT_UNTRACKED_COUNT="$(tail -n +2 <<< "${status}" | grep ^??  | wc -l | tr -d ' ')"


  if [ -z $SCM_BRANCH ]; then
	SCM_HEAD="${bash_prompt_green}$SCM_CHANGE"
  else
	SCM_HEAD="${bash_prompt_green}$SCM_BRANCH"
	if [ -z $SCM_GIT_UPSTREAM_REMOTE ]; then
	    SCM_HEAD="$SCM_HEAD${bash_prompt_cyan}(~)"
	elif [ "$SCM_GIT_UPSTREAM_BRANCH" == "$SCM_BRANCH" ]; then
	    SCM_HEAD="$SCM_HEAD${bash_prompt_cyan}($SCM_GIT_UPSTREAM_REMOTE)"
	else
	    SCM_HEAD="$SCM_HEAD${bash_prompt_cyan}($SCM_GIT_UPSTREAM_REMOTE/$SCM_GIT_UPSTREAM_BRANCH)"
	fi
	SCM_HEAD="$SCM_HEAD${bash_prompt_normal}:${bash_prompt_purple}$SCM_CHANGE"
  fi
}

function scm {
  if which git &> /dev/null && [[ -n "$(git rev-parse HEAD 2> /dev/null)" ]]; then
	git_prompt_vars
	SCM="${bash_prompt_green} |$SCM_HEAD"
	if [[ $SCM_GIT_STAGED_COUNT -gt 0 || $SCM_GIT_UNSTAGED_COUNT -gt 0 || $SCM_GIT_UNTRACKED_COUNT -gt 0 ]]; then
		SCM="$SCM ${bash_prompt_red}("
		[[ $SCM_GIT_STAGED_COUNT -gt 0 ]] && SCM="$SCM${bash_prompt_green}+"
		[[ $SCM_GIT_UNSTAGED_COUNT -gt 0 ]] && SCM="$SCM${bash_prompt_red}*"
		[[ $SCM_GIT_UNTRACKED_COUNT -gt 0 ]] && SCM="$SCM${bash_prompt_cyan}?"
		SCM="$SCM${bash_prompt_red})"
	else
		SCM="$SCM $SCM_CLEAN_SYMBOL"
	fi
	[[ $SCM_GIT_BEHIND -gt 0 ]] && SCM=" $SCM ${bash_prompt_red}$DOWN_ARROW_SYMBOL$SCM_GIT_BEHIND"
	[[ $SCM_GIT_AHEAD -gt 0 && $SCM_GIT_BEHIND -eq 0 ]] && SCM="$SCM${bash_prompt_cyan}"
	[[ $SCM_GIT_AHEAD -gt 0 ]] && SCM="$SCM $UP_ARROW_SYMBOL$SCM_GIT_AHEAD"
	[[ $SCM_GIT_STASH_COUNT -gt 0 ]] && SCM="$SCM ${bash_prompt_yellow}(stash: $SCM_GIT_STASH_COUNT)"
	SCM="$SCM${bash_prompt_green}|"
  else SCM=""
  fi
}


function prompt_command() {
	EXIT_STATUS=$?
	scm
	if [[ "$(dirs | wc -w)" -gt "1" ]]; then
		DIR_STACK=" ${bash_prompt_bold_cyan}$(dirs | wc -w)"
	else
		DIR_STACK=
	fi
	JOBS="$(jobs -l | perl -pe 's|(.+)Running\s+|\\[\\e[0;32m\\]\1 |g;' -pe 's|(.+)Stopped\s+|\\[\\e[0;31m\\]\1 |g;' -pe 's|(.+)Killed\s+|\\[\\e[0;35m\\]\1 |g;')"
	if [[ $EXIT_STATUS == 0 ]]; then
		EXIT_CODE=
	else
		EXIT_CODE="${bash_prompt_bold_white}${bash_prompt_background_red}!!! Exited: $EXIT_STATUS !!!"
	fi
	PS1="\n$JOBS\n${bash_prompt_yellow}\u${bash_prompt_normal}@\h ${bash_prompt_blue}[\w${DIR_STACK}${bash_prompt_blue}]$SCM ${bash_prompt_bold_red}\t $EXIT_CODE${bash_prompt_normal}\n ${bash_prompt_normal}\$ "
	# set title bar
	case "$TERM" in
		xterm*|rxvt*)
			PS1="\[\e]0;\u@\h: \w\a\]$PS1"
			;;
		*)
			;;
	esac
}
PROMPT_COMMAND=prompt_command;
##89-other.bashrc
# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"


function myps() { ps $@ -u $USER -o pid,%cpu,%mem,bsdtime,command ; }
function pstree() { myps f | awk '!/awk/ && $0~var' var=${1:-".*"} ; }


if [ -f ~/.local.bashrc ]; then
    source ~/.local.bashrc
fi



##90-archives.bashrc

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
