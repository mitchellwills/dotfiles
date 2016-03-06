(custom-set-variables
 '(inhibit-startup-screen t)
 '(uniquify-buffer-name-style (quote post-forward) nil (uniquify))
 '(vc-follow-symlinks t))
(custom-set-faces)

(setq backup-directory-alist `(("." . "~/.saves")))

(setq column-number-mode t)

(show-paren-mode 1)

(setq whitespace-style '(face empty tabs lines-tail trailing))
(global-whitespace-mode t)

(global-set-key (kbd "C-x |") 'split-window-horizontally)
(global-set-key (kbd "C-x _") 'split-window-vertically)
(global-set-key (kbd "C-x &") 'delete-window)

(add-to-list 'auto-mode-alist '("\\.launch$" . xml-mode))
(add-to-list 'auto-mode-alist '("\\.bashrc$" . shell-script-mode))
(add-to-list 'auto-mode-alist '("\\.zshrc$" . shell-script-mode))
(add-to-list 'auto-mode-alist '("\\.h\\'" . c++-mode))

(add-hook 'latex-mode-hook 'flyspell-mode)
(add-hook 'tex-mode-hook 'flyspell-mode)
(add-hook 'flyspell-mode-hook 'flyspell-buffer) ; spell check buffer on open

(global-set-key (kbd "<f7>") 'flyspell-buffer)

(setq-default indent-tabs-mode nil)

;; aligns annotation to the right hand side
(setq company-tooltip-align-annotations t)

(if (file-exists-p "~/\.local\.emacs")
    (load-file "~/.local.emacs"))
