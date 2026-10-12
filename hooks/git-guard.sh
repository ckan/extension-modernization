#!/bin/sh
# Pre-tool hook for Claude Code and Codex shell commands. In a CKAN extension
# project, git_guard.py holds back git commands that change the repository.
# Elsewhere, or without python3, every command passes.

. "${0%/*}/ckan-project.sh"

is_ckan_extension || exit 0
command -v python3 >/dev/null 2>&1 || exit 0
input=$(cat)
case $input in *git*) ;; *) exit 0 ;; esac
printf '%s' "$input" | python3 -I "${0%/*}/git_guard.py"
