(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(company-dabbrev-downcase nil)
 '(inhibit-startup-screen t)
 '(typescript-indent-level 2)
 '(uniquify-buffer-name-style (quote post-forward) nil (uniquify))
 '(vc-follow-symlinks t))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(company-scrollbar-bg ((t (:background "#191919"))))
 '(company-scrollbar-fg ((t (:background "#0c0c0c"))))
 '(company-tooltip ((t (:inherit default :background "#050505"))))
 '(company-tooltip-common ((t (:inherit font-lock-constant-face))))
 '(company-tooltip-selection ((t (:inherit font-lock-function-name-face)))))

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

(add-hook 'after-init-hook 'global-company-mode)
(setq company-idle-delay 0)

(if (file-exists-p "~/\.local\.emacs")
    (load-file "~/.local.emacs"))
