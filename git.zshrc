function build_git_prompt {
    local git_status_lines
    IFS=$'\n' git_status_lines=($(git status -bs --porcelain 2> /dev/null))
    local git_stash_list_lines
    IFS=$'\n' git_stash_list_lines=($(git stash list 2> /dev/null))

    local SCM_GIT_DIR=$(git rev-parse --git-dir 2>/dev/null)
    local ref=$(git symbolic-ref HEAD 2> /dev/null)
    SCM_BRANCH=${ref#refs/heads/}
    SCM_CHANGE=$(git rev-parse HEAD 2>/dev/null)
    SCM_CHANGE_SHORT=$(git rev-parse --short HEAD 2>/dev/null)

    # Check for publish branches
    SCM_PUBLISHED_CHANGE=""
    if [ -n "$SCM_BRANCH" ]; then
      SCM_PUBLISHED_CHANGE=$(git rev-parse --verify --quiet "refs/exported/$SCM_BRANCH^0" 2>/dev/null)
      if [[ -z "$SCM_PUBLISHED_CHANGE" ]]; then
        SCM_PUBLISHED_CHANGE=$(git rev-parse --verify --quiet "refs/published/$SCM_BRANCH^0" 2>/dev/null)
      fi
    fi

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
	SCM_HEAD="%F{green}$SCM_CHANGE_SHORT"
    else
	SCM_HEAD="%F{green}$SCM_BRANCH"
	if [[ $SCM_GIT_UPSTREAM_REMOTE == "" ]]; then
	    SCM_HEAD="$SCM_HEAD%F{cyan}(~)"
	elif [[ "$SCM_GIT_UPSTREAM_BRANCH" == "$SCM_BRANCH" ]]; then
	    SCM_HEAD="$SCM_HEAD%F{cyan}($SCM_GIT_UPSTREAM_REMOTE)"
	else
	    SCM_HEAD="$SCM_HEAD%F{cyan}($SCM_GIT_UPSTREAM_REMOTE/$SCM_GIT_UPSTREAM_BRANCH)"
	fi
	SCM_HEAD="$SCM_HEAD%F{white}:%F{magenta}$SCM_CHANGE_SHORT"
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

    local git_mode=""
    if [[ -e "$SCM_GIT_DIR/MERGE_HEAD" ]]; then
      git_mode=" $fg_bold[red]MERGE"
    elif [[ -e "$SCM_GIT_DIR/rebase" || -e "$SCM_GIT_DIR/rebase-apply" || -e "$SCM_GIT_DIR/rebase-merge" ]]; then
      git_mode=" $fg_bold[red]REBASE"
    fi

    local git_remote_state=""
    [[ $SCM_GIT_BEHIND -gt 0 ]] && git_remote_state="$git_remote_state%F{red} $DOWN_ARROW_SYMBOL$SCM_GIT_BEHIND"
    [[ $SCM_GIT_AHEAD -gt 0 && $SCM_GIT_BEHIND -eq 0 ]] && git_remote_state="$git_remote_state%F{cyan}"
    [[ $SCM_GIT_AHEAD -gt 0 ]] && git_remote_state="$git_remote_state $UP_ARROW_SYMBOL$SCM_GIT_AHEAD"

    local git_stash_state=""
    [[ $SCM_GIT_STASH_COUNT -gt 0 ]] && git_stash_state=" %F{yellow}(stash: $SCM_GIT_STASH_COUNT)"

    local git_publish_state=""
    if [ -n "$SCM_PUBLISHED_CHANGE" ]; then
      if [[ "$SCM_CHANGE" == "$SCM_PUBLISHED_CHANGE" ]]; then
        git_publish_state=" %F{green}$UP_TRIANGLE_FILLED_SYMBOL"
      else
        git_publish_state=" %F{red}$UP_TRIANGLE_SYMBOL"
      fi
    fi

    PROMPT_SCM="%F{green} |$PLUS_MINUS_SYMBOL $SCM_HEAD $git_wc_state$git_remote_state$git_stash_state$git_publish_state$git_mode%F{green}|"
}
