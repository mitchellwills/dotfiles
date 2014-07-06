(custom-set-variables
 '(inhibit-startup-screen t)
 '(vc-follow-symlinks t))
(custom-set-faces
 )

(setq auto-mode-alist (cons '("\\.launch$" . xml-mode) auto-mode-alist))
(setq auto-mode-alist (cons '("\\.bashrc$" . shell-script-mode) auto-mode-alist))

(global-set-key (kbd "C-x |") 'split-window-horizontally)
(global-set-key (kbd "C-x _") 'split-window-vertically)
(global-set-key (kbd "C-x &") 'delete-window)

(global-font-lock-mode 1)

(add-to-list 'load-path "~/.emacs.d/")
(load "move-border.el")

(require 'move-border)
(global-set-key (kbd "C-x M-[ a") 'move-border-up)
(global-set-key (kbd "C-x M-[ b") 'move-border-down)
(global-set-key (kbd "C-x M-[ d") 'move-border-left)
(global-set-key (kbd "C-x M-[ c") 'move-border-right)
