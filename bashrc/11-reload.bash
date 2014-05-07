function reload-dotfiles(){
  cd ~/.dotfiles
  git pull
  ./install.sh
  source ~/.bashrc
}
