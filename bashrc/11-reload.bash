function reload-dotfiles(){
(
  cd ~/.dotfiles
  git pull
  ./install.py --no-install
  source ~/.bashrc
)
}
