(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(inhibit-startup-screen t)
 '(uniquify-buffer-name-style (quote post-forward) nil (uniquify))
 '(vc-follow-symlinks t))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

(setq column-number-mode t)

(show-paren-mode 1)

(add-hook 'after-init-hook #'global-flycheck-mode)

(setq-default show-trailing-whitespace t)

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

(require 'uniquify)
(require 'package)
(setq package-archives '(("gnu" . "http://elpa.gnu.org/packages/")
                         ("marmalade" . "http://marmalade-repo.org/packages/")
                         ("melpa" . "http://melpa.milkbox.net/packages/")))
(package-initialize)

(load-theme 'wombat t)
