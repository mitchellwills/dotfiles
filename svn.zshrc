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

    PROMPT_SCM="%F{green} |$LIGHTNING_BOLT_SYMBOL $SCM_HEAD $svn_wc_state%F{green}|"
}
