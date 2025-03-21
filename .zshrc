osname=`uname`

TMPPREFIX=/tmp/zsh
mkdir -p $TMPPREFIX

autoload bashcompinit
bashcompinit

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
autoload -Uz compinit && compinit
# enables Shift-Tab backwards autocompletion
bindkey '^[[Z' reverse-menu-complete

# Setup programs
export EDITOR='emacs -nw'
export PAGER=less
export LESS=FRX

setopt PROMPT_SUBST



DOWN_ARROW_SYMBOL=$'\xe2\x86\x93'
RIGHT_ARROW_SYMBOL=$'\xe2\x86\x92'
UP_ARROW_SYMBOL=$'\xe2\x86\x91'
LEFT_ARROW_SYMBOL=$'\xe2\x86\x90'
PLUS_MINUS_SYMBOL=$'±'
LIGHTNING_BOLT_SYMBOL=$'⚡'
X_SYMBOL="✗"
CHECK_SYMBOL="✓"
UP_TRIANGLE_FILLED_SYMBOL="▲"
UP_TRIANGLE_SYMBOL="△"

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

    PROMPT_WD=${PWD/#$HOME/'~'}

    PROMPT_SCM=""
    local_precmd

    # fill in the bits of prompt that can be done very quickly (e.g. from cwd)
    for fn in "${PROMPT_SCM_HANDLERS[@]}"; do
      if $fn 'fast'; then
        break
      fi
    done

    PROMPT_ASYNC="$PROMPT_SCM"
    async-build-prompt &!
}
function local_precmd {} # to be overridden by local script

unset PROMPT_SCM_HANDLERS
PROMPT_SCM_HANDLERS=()

function async-build-prompt {
  # SCM
  PROMPT_SCM=""
  for fn in "${PROMPT_SCM_HANDLERS[@]}"; do
    if $fn; then
      break
    fi
  done

  printf "%s" "$PROMPT_SCM" > ${TMPPREFIX}/prompt-delay.$$

  # Tell shell to update prompt
  kill -SIGUSR2 $$
}

# callback from child process
function TRAPUSR2 {
    PROMPT_ASYNC=$(cat "${TMPPREFIX}/prompt-delay.$$")
    # Redisplay prompt
    zle && zle reset-prompt
}

PROMPT=$'\n$PROMPT_EXIT_STATUS$PROMPT_JOBS%F{yellow}%n%F{white}@$PROMPT_MACHINE_PREFIX%m %F{blue}[$PROMPT_WD]%{$reset_color%}$PROMPT_ASYNC\n%F{cyan}%h %{$reset_color%}%(!.#.$) '

source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

source ~/.dotfiles/aliases.zshrc
source ~/.dotfiles/git.zshrc
source ~/.dotfiles/svn.zshrc

if [ -f ~/.local.zshrc ]; then
    source ~/.local.zshrc
fi
