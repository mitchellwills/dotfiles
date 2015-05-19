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
# enables Shift-Tab backwards autocompletion
bindkey '^[[Z' reverse-menu-complete

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

SCM_DIRTY_SYMBOL="%F{red}$X_SYMBOL"
SCM_CLEAN_SYMBOL="%F{green}$CHECK_SYMBOL"

precmd() {
    # Handle previous command exit code
    local exitcode=$?
    if [[ $exitcode -eq 0 ]]
    then
	PROMPT_EXIT_STATUS=""
    else
	if [[ $exitcode -eq 127 ]]; then
	    PROMPT_EXIT_STATUS="Command Not Found"
	elif [[ $exitcode -ge 128 && $exitcode -le (127+${#signals}) ]]; then
	    PROMPT_EXIT_STATUS="SIG$signals[$exitcode-127]"
	else
	    PROMPT_EXIT_STATUS="Exited: $exitcode"
	fi
	PROMPT_EXIT_STATUS="%F{red}!!!!!!!!!! $PROMPT_EXIT_STATUS !!!!!!!!!!%{$reset_color%}"$'\n'
    fi

    PROMPT_MACHINE_PREFIX=""
    if [[ $INSIDE_EMACS != '' ]]; then
	PROMPT_MACHINE_PREFIX="${PROMPT_MACHINE_PREFIX}emacs/"
    fi
    if [[ $TMUX != '' ]]; then
	# slice removes percent from beginning of TMUX_PANE
	PROMPT_MACHINE_PREFIX="${PROMPT_MACHINE_PREFIX}tmux[${TMUX_PANE[2,-1]}]/"
    fi
    if [[ $SSH_CLIENT != '' ]]; then
	PROMPT_MACHINE_PREFIX="${PROMPT_MACHINE_PREFIX}ssh/"
    fi

    PROMPT_JOBS=""
    for id in ${(k)jobstates}; do
	local upstream_re='.+\.\.\.([[:print:]]+)/([^[:space:]]+)'
	local job_state="?"
	local job_mark=""
	local job_pid="????"
	if [[ "${jobstates[$id]}" =~ '([^:]+):([^:]*):([^=]+)=(.+)' ]]; then
	    job_state=$match[1]
	    job_mark=$match[2]
	    job_pid=$match[3]
	    job_process_state=$match[4]
	fi
	if [[ $job_mark == "" ]]; then
	    job_mark=" "
	fi
	if [[ $job_state == 'running' ]]; then
	    job_color="%F{green}"
	elif [[ $job_state == 'suspended' ]]; then
	    job_color="%F{red}"
	elif [[ $job_state == 'done' ]]; then
	    job_color="%F{magenta}"
	else
	    job_color="%F{white}"
	fi
	PROMPT_JOBS="${PROMPT_JOBS}${job_color}[$id]$job_mark $job_pid $jobtexts[$id]"$'\n'
    done

    # Set terminal title
    case "$TERM" in
	xterm*|rxvt*)
	    print -Pn "\e]0;%n@%m: %~\a"
	    ;;
	*)
	    ;;
    esac


    PROMPT_ASYNC=""
    async-build-prompt &!
}



function build_git_prompt {
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

    local git_wc_state=""
    if [[ $SCM_GIT_STAGED_COUNT -gt 0 || $SCM_GIT_UNSTAGED_COUNT -gt 0 || $SCM_GIT_UNTRACKED_COUNT -gt 0 ]]; then
	git_wc_state="%F{red}("
	[[ $SCM_GIT_STAGED_COUNT -gt 0 ]] && git_wc_state="$git_wc_state%F{green}+"
	[[ $SCM_GIT_UNSTAGED_COUNT -gt 0 ]] && git_wc_state="$git_wc_state%F{red}*"
	[[ $SCM_GIT_UNTRACKED_COUNT -gt 0 ]] && git_wc_state="$git_wc_state%F{cyan}?"
	git_wc_state="$git_wc_state%F{red})"
    else
	git_wc_state="$SCM_CLEAN_SYMBOL"
    fi

    local git_remote_state=""
    [[ $SCM_GIT_BEHIND -gt 0 ]] && git_remote_state="$git_remote_state%F{red} $DOWN_ARROW_SYMBOL$SCM_GIT_BEHIND"
    [[ $SCM_GIT_AHEAD -gt 0 && $SCM_GIT_BEHIND -eq 0 ]] && git_remote_state="$git_remote_state%F{cyan}"
    [[ $SCM_GIT_AHEAD -gt 0 ]] && git_remote_state="$git_remote_state $UP_ARROW_SYMBOL$SCM_GIT_AHEAD"

    local git_stash_state=""
    [[ $SCM_GIT_STASH_COUNT -gt 0 ]] && git_stash_state=" %F{yellow}(stash: $SCM_GIT_STASH_COUNT)"

    PROMPT_SCM="%F{green} |$PLUS_MINUS_SYMBOL $SCM_HEAD $git_wc_state$git_remote_state$git_stash_state%F{green}|"
}
function build_svn_prompt {
    local svn_info_lines
    svn_info_lines=("${(@f)$(svn info 2> /dev/null)}")

    local svn_status_lines
    svn_status_lines=("${(@f)$(svn status 2> /dev/null)}")

    local svn_revision="?"
    local svn_branch=""

    for info in $svn_info_lines; do
	if [[ "$info" =~ 'Revision: (.+)' ]]; then
	    svn_revision=$match[1]
	elif [[ "$info" =~ 'Relative URL: \^/(.+)' ]]; then
	    svn_branch=$match[1]
	fi
    done

    local svn_untracked_count=0
    local svn_uncommitted_count=0
    for line in $svn_status_lines; do
	if [[ "$line" =~ '(.)(.)(.)(.)(.)(.)(.) (.+)' ]]; then
	    local file_change_state=$match[1]
	    local file_tree_conflict=$match[7]

	    if [[ $file_tree_conflict != " " && $file_tree_conflict != "C" ]]; then
		continue
	    fi

	    if [[ $file_change_state == ' ' ]]; then
		# file not modified
	    elif [[ $file_change_state == '?' ]]; then
      		((++svn_untracked_count))
	    else
      		((++svn_uncommitted_count))
	    fi
	fi
    done

    local svn_wc_state=""
    if [[ $svn_untracked_count -gt 0 || $svn_uncommitted_count -gt 0 ]]; then
	svn_wc_state="%F{red}("
	[[ $svn_uncommitted_count -gt 0 ]] && svn_wc_state="$svn_wc_state%F{red}*"
	[[ $svn_untracked_count -gt 0 ]] && svn_wc_state="$svn_wc_state%F{cyan}?"
	svn_wc_state="$svn_wc_state%F{red})"
    else
	svn_wc_state="$SCM_CLEAN_SYMBOL"
    fi

    if [ -z $svn_branch ]; then
	SCM_HEAD="%F{green}$svn_revision"
    else
	SCM_HEAD="%F{green}$svn_branch%F{white}:%F{magenta}$svn_revision"
    fi

    PROMPT_SCM="%F{green} |svn $SCM_HEAD $svn_wc_state%F{green}|"
}
function async-build-prompt {
    # SCM
    if which git &> /dev/null && [[ -n "$(git rev-parse HEAD 2> /dev/null)" ]]; then
	build_git_prompt
    elif which svn &> /dev/null && [[ -n "$(svn info 2> /dev/null)" ]]; then
	build_svn_prompt
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

PROMPT=$'\n$PROMPT_EXIT_STATUS$PROMPT_JOBS%F{yellow}%n%F{white}@$PROMPT_MACHINE_PREFIX%m %F{blue}[%~]%{$reset_color%}$PROMPT_ASYNC\n%F{cyan}%h %{$reset_color%}%(!.#.$) '



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
