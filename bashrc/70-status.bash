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
