jj_log_template='concat('\
'change_id.shortest(6), "|", '\
'commit_id.shortest(6), "|", '\
'description.len(), "|", '\
'stringify(current_working_copy), "|", '\
'stringify(empty), "|", '\
'stringify(conflict), "|", '\
'self.contained_in("trunk()"), "|", '\
'separate(",", stringify(remote_bookmarks.join(",")), EXTRA_REMOTE_BOOKMARKS), "\n", '\
')'

function build_jj_prompt {
    # don't support fast prompt generation
    if [[ $1 == 'fast' ]]; then return 1; fi

    if ! which jj &> /dev/null; then return 1; fi

    if ! jj op log -n 1 --no-graph --color=never --ignore-working-copy &>/dev/null; then
        return 1
    fi

    LOCAL_BOOKMARK_NAME="$2"
    EXTRA_REMOTE_BOOKMARKS="$3"
    REWRITE_TRUNK_REMOTE_BOOKMARKS="$4"

    local log_lines
    IFS=$'\n' log_lines=($(jj log  \
      --color=always --no-graph  \
      --ignore-working-copy  \
      -r 'trunk()::@'  \
      -T "${jj_log_template/EXTRA_REMOTE_BOOKMARKS/$EXTRA_REMOTE_BOOKMARKS}"  \
      ))

    SCM_JJ_TRUNK_CHANGE_ID=""
    SCM_JJ_TRUNK_BOOKMARKS=()
    SCM_JJ_UNCOMMITED="false"
    SCM_JJ_NON_TRUNK_CHANGES=0
    SCM_JJ_WC_CHANGE_ID=""
    SCM_JJ_WC_COMMIT_ID=""
    SCM_JJ_CONFLICT="false"

    for raw_line in "${log_lines[@]}"; do
      IFS='|' log_line=($raw_line)

      change_id="$log_line[1]"
      commit_id="$log_line[2]"
      description_length="$log_line[3]"
      current_working_copy="$log_line[4]"
      empty="$log_line[5]"
      conflict="$log_line[6]"
      trunk="$log_line[7]"
      IFS=',' remote_bookmarks=($log_line[8])

      if [ "$trunk" = true ]; then
        if [[ -z "$SCM_JJ_TRUNK_CHANGE_ID" ]]; then
          SCM_JJ_TRUNK_CHANGE_ID="$change_id"

          for bookmark in "${remote_bookmarks[@]}"; do
            if ! [[ "$bookmark" =~ '@git$' ]]; then
              SCM_JJ_TRUNK_BOOKMARKS+="$bookmark"
            fi
          done
        fi
      else
        if [ "$conflict" = true ]; then SCM_JJ_CONFLICT=true; fi
        if [ "$current_working_copy" = true ]; then
          SCM_JJ_WC_CHANGE_ID="$change_id"
          SCM_JJ_WC_COMMIT_ID="$commit_id"
        fi

        if [[ "$description_length" = 0 && "$current_working_copy" = true ]]; then
          SCM_JJ_UNCOMMITED=true
        else
          ((++SCM_JJ_NON_TRUNK_CHANGES))
        fi
      fi
    done

    SCM_HEAD=""
    if [[ "$LOCAL_BOOKMARK_NAME" != '' ]]; then
      SCM_HEAD="%F{green}$LOCAL_BOOKMARK_NAME"
    fi
    if [[ -z $SCM_JJ_TRUNK_BOOKMARKS ]]; then
      SCM_HEAD+="%F{cyan}($SCM_JJ_TRUNK_CHANGE_ID%F{cyan})"
    else
      $REWRITE_TRUNK_REMOTE_BOOKMARKS
      IFS=',' SCM_HEAD+="%F{cyan}(%F{cyan}${SCM_JJ_TRUNK_BOOKMARKS[*]})"
    fi
    SCM_HEAD+="%F{white}:$SCM_JJ_WC_CHANGE_ID%F{white}:$SCM_JJ_WC_COMMIT_ID"

    local jj_wc_state=""
    if [ "$SCM_JJ_UNCOMMITED" = true ]; then
      jj_wc_state="%F{red}(*)"
    else
      jj_wc_state="$SCM_CLEAN_SYMBOL"
    fi
    if [ "$SCM_JJ_CONFLICT" = true ]; then
      jj_wc_state+=" $fg_bold[red]CONFLICT"
    fi

    local jj_trunk_state=""
    [[ "$SCM_JJ_NON_TRUNK_CHANGES" -gt 0 ]] && jj_trunk_state+=" %F{cyan}$UP_ARROW_SYMBOL$SCM_JJ_NON_TRUNK_CHANGES"

    PROMPT_SCM="%F{green} |🐦 $SCM_HEAD $jj_wc_state$jj_trunk_state%F{green}|"
}

PROMPT_SCM_HANDLERS=(build_jj_prompt ${PROMPT_SCM_HANDLERS[@]})
