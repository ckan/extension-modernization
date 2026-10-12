#!/bin/sh
# Session-start hook for Claude Code and Codex. In a CKAN extension project it
# prints a one-line reminder, which the client adds to the agent's context.
# It prints nothing in other projects, including a CKAN core checkout.

. "${0%/*}/ckan-project.sh"

is_ckan_extension || exit 0
echo "This project contains CKAN extension code. Before exploring or editing it," \
    "load the matching skill from the extension-modernization plugin, even for" \
    "small tasks: the one the user names, otherwise ckan-development for changes" \
    "and questions, ckan-plan for planning, ckan-review for reviews."
