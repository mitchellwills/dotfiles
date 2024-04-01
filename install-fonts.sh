#!/usr/bin/env bash

set -e
set -x

LOCAL_FONT_DIR="$HOME/.local/share/fonts"
mkdir -p "$LOCAL_FONT_DIR"

CASCADIA_CODE_ARCHIVE="$(mktemp -u /tmp/CascadiaCode.XXX.zip)"
curl -fLo "$CASCADIA_CODE_ARCHIVE" "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.1.1/CascadiaCode.zip"
unzip "$CASCADIA_CODE_ARCHIVE" '*.ttf' -d "$LOCAL_FONT_DIR"
rm "$CASCADIA_CODE_ARCHIVE"

fc-cache -f -v
