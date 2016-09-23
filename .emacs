
;; Added by Package.el.  This must come before configurations of
;; installed packages.  Don't delete this line.  If you don't want it,
;; just comment it out by adding a semicolon to the start of the line.
;; You may delete these explanatory comments.
(package-initialize)

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(company-dabbrev-downcase nil)
 '(inhibit-startup-screen t)
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

(global-set-key (kbd "M-n") (lambda () (interactive) (next-line 15)))
(global-set-key (kbd "M-p") (lambda () (interactive) (previous-line 15)))

(add-to-list 'auto-mode-alist '("\\.launch$" . xml-mode))
(add-to-list 'auto-mode-alist '("\\.bashrc$" . shell-script-mode))
(add-to-list 'auto-mode-alist '("\\.zshrc$" . shell-script-mode))
(add-to-list 'auto-mode-alist '("\\.h\\'" . c++-mode))
(add-to-list 'auto-mode-alist '("\\.ng\\'" . html-mode))

(add-hook 'markdown-mode-hook 'flyspell-mode)
(add-hook 'latex-mode-hook 'flyspell-mode)
(add-hook 'tex-mode-hook 'flyspell-mode)
(add-hook 'text-mode-hook 'flyspell-mode)
(add-hook 'prog-mode-hook 'flyspell-prog-mode)

(global-set-key (kbd "<f7>") 'flyspell-buffer)

(setq-default indent-tabs-mode nil)

;; aligns annotation to the right hand side
(setq company-tooltip-align-annotations t)

(add-hook 'after-init-hook 'global-company-mode)
(setq company-idle-delay 0.05)

(if (file-exists-p "~/\.local\.emacs")
    (load-file "~/.local.emacs"))
