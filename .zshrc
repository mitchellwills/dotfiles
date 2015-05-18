TMPPREFIX=/tmp/zsh
mkdir -p $TMPPREFIX

setopt correct
setopt autocd
setopt nomatch
setopt extendedglob

# Setup key bindings
bindkey -e # set key binding to emacs mode
WORDCHARS=${WORDCHARS/\/} # don't consider forward slash part of a word

# Setup history
HISTFILE=~/.zsh_history
setopt APPEND_HISTORY
HISTSIZE=1000
SAVEHIST=1000
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE

# Initialize colors
autoload -U colors && colors


# Initialize autocompletion
#zstyle :compinstall filename '/home/mitchell/.zshrc'
autoload -Uz compinit && compinit

# Setup programs
export EDITOR='emacs -nw'
export PAGER=less

setopt PROMPT_SUBST



DOWN_ARROW_SYMBOL=$'\xe2\x86\x93'
RIGHT_ARROW_SYMBOL=$'\xe2\x86\x92'
UP_ARROW_SYMBOL=$'\xe2\x86\x91'
LEFT_ARROW_SYMBOL=$'\xe2\x86\x90'
PLUS_MINUS_SYMBOL=$'±'
X_SYMBOL="✗"
CHECK_SYMBOL="✓"

SCM_SYMBOL=$PLUS_MINUS_SYMBOL
SCM_DIRTY_SYMBOL="%F{red}$X_SYMBOL"
SCM_CLEAN_SYMBOL="%F{green}$CHECK_SYMBOL"

function git_prompt_vars {
  # the assignment of these must be on the following line
  local git_status_lines
  git_status_lines=("${(@f)$(git status -bs --porcelain 2> /dev/null)}")
  local git_stash_list_lines
  git_stash_list_lines=("${(@f)$(git stash list 2> /dev/null)}")

  local ref=$(git symbolic-ref HEAD 2> /dev/null)
  SCM_BRANCH=${ref#refs/heads/}
  SCM_CHANGE=$(git rev-parse --short HEAD 2>/dev/null)

  SCM_GIT_AHEAD=''
  SCM_GIT_BEHIND=''
  local ahead_re='.+ahead ([0-9]+).+'
  local behind_re='.+behind ([0-9]+).+'
  [[ "${git_status_lines[1]}" =~ ${ahead_re} ]] && SCM_GIT_AHEAD="${match[1]}"
  [[ "${git_status_lines[1]}" =~ ${behind_re} ]] && SCM_GIT_BEHIND="${match[1]}"

  SCM_GIT_UPSTREAM_REMOTE=''
  SCM_GIT_UPSTREAM_BRANCH=''
  local upstream_re='.+\.\.\.([[:print:]]+)/([^[:space:]]+)'
  [[ "${git_status_lines[1]}" =~ ${upstream_re} ]] && SCM_GIT_UPSTREAM_REMOTE="${match[1]}" && SCM_GIT_UPSTREAM_BRANCH="${match[2]}"

  if [[ $git_stash_list_lines[1] == '' ]]; then
      SCM_GIT_STASH_COUNT=0
  else
      SCM_GIT_STASH_COUNT=$#git_stash_list_lines
  fi

  SCM_GIT_STAGED_COUNT=0
  SCM_GIT_UNSTAGED_COUNT=0
  SCM_GIT_UNTRACKED_COUNT=0
  for l in ${git_status_lines[2,-1]}; do
      if [[ $l[1,2] = '??' ]]; then
	  ((++SCM_GIT_UNTRACKED_COUNT))
      else
	  if [[ $l[1] != ' ' ]]; then
      	      ((++SCM_GIT_STAGED_COUNT))
	  fi
	  if [[ $l[2] != ' ' ]]; then
      	      ((++SCM_GIT_UNSTAGED_COUNT))
	  fi
      fi
  done

  if [ -z $SCM_BRANCH ]; then
	SCM_HEAD="%F{green}$SCM_CHANGE"
  else
	SCM_HEAD="%F{green}$SCM_BRANCH"
	if [[ $SCM_GIT_UPSTREAM_REMOTE == "" ]]; then
	    SCM_HEAD="$SCM_HEAD%F{cyan}(~)"
	elif [[ "$SCM_GIT_UPSTREAM_BRANCH" == "$SCM_BRANCH" ]]; then
	    SCM_HEAD="$SCM_HEAD%F{cyan}($SCM_GIT_UPSTREAM_REMOTE)"
	else
	    SCM_HEAD="$SCM_HEAD%F{cyan}($SCM_GIT_UPSTREAM_REMOTE/$SCM_GIT_UPSTREAM_BRANCH)"
	fi
	SCM_HEAD="$SCM_HEAD%F{white}:%F{magenta}$SCM_CHANGE"
  fi
}


precmd() {
    # Handle previous command exit code
    local exitcode=$?
    if [[ $exitcode -eq 0 ]]
    then
	PROMPT_EXIT_STATUS=""
    elif [[ $exitcode -eq 127 ]]
    then
	PROMPT_EXIT_STATUS="%K{red}%F{white}%B!!! Command Not Found !!!%{$reset_color%}"$'\n'
    elif [[ $exitcode -ge 128 && $exitcode -le (127+${#signals}) ]]
    then
	PROMPT_EXIT_STATUS="%K{red}%F{white}%B!!! SIG$signals[$exitcode-127] !!!%{$reset_color%}"$'\n'
    else
	PROMPT_EXIT_STATUS="%K{red}%F{white}%B!!! Exited: $exitcode !!!%{$reset_color%}"$'\n'
    fi

    PROMPT_ASYNC=""
    async-build-prompt &!
}
function async-build-prompt {
    # SCM
    if which git &> /dev/null && [[ -n "$(git rev-parse HEAD 2> /dev/null)" ]]; then
	git_prompt_vars
	PROMPT_SCM="%F{green} |$SCM_HEAD"
	if [[ $SCM_GIT_STAGED_COUNT -gt 0 || $SCM_GIT_UNSTAGED_COUNT -gt 0 || $SCM_GIT_UNTRACKED_COUNT -gt 0 ]]; then
	    PROMPT_SCM="$PROMPT_SCM %F{red}("
	    [[ $SCM_GIT_STAGED_COUNT -gt 0 ]] && PROMPT_SCM="$PROMPT_SCM%F{green}+"
	    [[ $SCM_GIT_UNSTAGED_COUNT -gt 0 ]] && PROMPT_SCM="$PROMPT_SCM%F{red}*"
	    [[ $SCM_GIT_UNTRACKED_COUNT -gt 0 ]] && PROMPT_SCM="$PROMPT_SCM%F{cyan}?"
	    PROMPT_SCM="$PROMPT_SCM%F{red})"
	else
	    PROMPT_SCM="$PROMPT_SCM $SCM_CLEAN_SYMBOL"
	fi
	[[ $SCM_GIT_BEHIND -gt 0 ]] && PROMPT_SCM=" $PROMPT_SCM %F{red}$DOWN_ARROW_SYMBOL$SCM_GIT_BEHIND"
	[[ $SCM_GIT_AHEAD -gt 0 && $SCM_GIT_BEHIND -eq 0 ]] && PROMPT_SCM="$PROMPT_SCM%F{cyan}"
	[[ $SCM_GIT_AHEAD -gt 0 ]] && PROMPT_SCM="$PROMPT_SCM $UP_ARROW_SYMBOL$SCM_GIT_AHEAD"
	[[ $SCM_GIT_STASH_COUNT -gt 0 ]] && PROMPT_SCM="$PROMPT_SCM %F{yellow}(stash: $SCM_GIT_STASH_COUNT)"
	PROMPT_SCM="$PROMPT_SCM%F{green}|"
    else
	PROMPT_SCM=""
    fi

    printf "%s" $PROMPT_SCM > ${TMPPREFIX}/prompt-delay.$$

    # Tell shell to update prompt
    kill -SIGUSR2 $$
}
# callback from child process
function TRAPUSR2 {
    PROMPT_ASYNC=$(cat "${TMPPREFIX}/prompt-delay.$$")
    # Redisplay prompt
    zle && zle reset-prompt
}

PROMPT=$'\n$PROMPT_EXIT_STATUS%F{yellow}%n%F{white}@%m %F{blue}[%~]%{$reset_color%}$PROMPT_ASYNC\n%F{cyan}%h %{$reset_color%}%(!.#.$) '



######## SETUP ALIASES ##########
alias emacs='emacs -nw'		# make emacs only run in the terminal

# Directory aliases
alias -- -='cd -'		# go to the previous directory
alias -g ...='../..'
alias -g ....='../../..'
alias -g .....='../../../..'
alias -g ......='../../../../..'

alias l='ls'
alias less='less -R'
alias ll='l -Al'
alias lll='ll -a'
alias llll='lll -i'
alias lr='ll -R'		# Recursive ls
alias ls='ls -h -F --color=auto'

alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'

alias df='df -h'
alias du='du -h'
alias grep-rec='find . -type f -print0 | xargs -0 grep'

alias killbg='kill $(jobs -p)'		# kill all background tasks

alias mkdir='mkdir -p'		# recursive directory make
alias rmtmp='rm -f *~;rm -f .*~'		# delete all file ending in ~ in the current directory
alias tree='tree -aChsu'		# Nice alternative to recursive ls
alias webserver='python -m SimpleHTTPServer'		# Simple web server
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
