"""Hold back git commands that change a CKAN extension's repository.

Reads a PreToolUse hook payload on stdin. Read-only git commands pass
silently. Any other git command gets an "ask" decision in Claude Code and a
"deny" decision in Codex, which does not support "ask". This is a guardrail,
not a security boundary: git run from scripts, aliases, or build tools is not
seen.
"""

from __future__ import annotations

import json
import os
import shlex
import sys

READ_ONLY = {
    "blame", "cat-file", "check-attr", "check-ignore", "count-objects", "describe", "diff",
    "diff-files", "diff-index", "diff-tree", "for-each-ref", "grep", "help", "log", "ls-files",
    "ls-tree", "merge-base", "name-rev", "range-diff", "rev-list", "rev-parse", "shortlog",
    "show", "show-ref", "status", "var", "version", "whatchanged",
}
# Subcommands that only read in these forms: (subcommand, first non-option word).
READ_FORMS = {
    ("remote", ""), ("remote", "show"), ("remote", "get-url"), ("stash", "list"),
    ("stash", "show"), ("worktree", "list"), ("reflog", ""), ("reflog", "show"),
    ("reflog", "exists"),
}
LIST_FLAGS = {"-l", "--list", "--contains", "--no-contains", "--merged", "--no-merged",
              "--points-at"}
BRANCH_WRITES = {"-d", "-D", "--delete", "-m", "-M", "--move", "-c", "-C", "--copy", "-f",
                 "--force", "-u", "--set-upstream-to", "--unset-upstream",
                 "--edit-description", "-t", "--track", "--no-track", "--create-reflog"}
TAG_WRITES = {"-a", "--annotate", "-s", "--sign", "-u", "--local-user", "-f", "--force", "-d",
              "--delete", "-m", "--message", "-F", "--file", "-e", "--edit", "--create-reflog"}
CONFIG_READS = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "-l", "--list"}
CONFIG_WRITES = {"--add", "--unset", "--unset-all", "--replace-all", "--rename-section",
                 "--remove-section", "-e", "--edit"}
GLOBAL_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env",
                "--super-prefix"}
# Long options whose value may follow as a separate argument.
OPTION_VALUE = {"--format", "--sort", "--contains", "--no-contains", "--merged", "--no-merged",
                "--points-at", "--file", "--blob"}
KEYWORDS = {"if", "then", "elif", "else", "do", "while", "until", "!", "{"}
WRAPPERS = {"command", "env", "exec", "nice", "nohup", "sudo", "time", "timeout", "xargs"}
SHELLS = {"bash", "dash", "ksh", "sh", "zsh"}
OPERATORS = set("();<>|&")


def options(args: list[str]) -> tuple[set[str], list[str]]:
    """Split arguments into option names and other words.

    Combined or attached short options, such as -vv or -uorigin/main, count as
    every letter they contain, so a write flag cannot hide in them.
    """
    flags: set[str] = set()
    words: list[str] = []
    remaining = iter(args)
    for arg in remaining:
        if arg.startswith("--"):
            name = arg.split("=", 1)[0]
            flags.add(name)
            if name in OPTION_VALUE and "=" not in arg:
                next(remaining, None)
        elif arg.startswith("-") and len(arg) > 1:
            flags.update(f"-{letter}" for letter in arg[1:])
        else:
            words.append(arg)
    return flags, words


def reads_only(sub: str, args: list[str]) -> bool:
    """Return whether a git subcommand with these arguments only reads."""
    if sub in READ_ONLY:
        return True
    flags, words = options(args)
    if sub in ("branch", "tag"):
        writes = BRANCH_WRITES if sub == "branch" else TAG_WRITES
        return not flags & writes and (not words or bool(flags & LIST_FLAGS))
    if sub == "config":
        if flags & CONFIG_WRITES or (words and words[0] in
                                     {"set", "unset", "rename-section", "remove-section", "edit"}):
            return False
        return bool(flags & CONFIG_READS) or (words[:1] in (["get"], ["list"])) or len(words) <= 1
    return (sub, words[0] if words else "") in READ_FORMS


def git_allowed(args: list[str]) -> bool:
    """Return whether a git invocation, given its arguments, only reads."""
    index = 0
    while index < len(args) and args[index].startswith("-"):
        if args[index] in ("--version", "--help", "-h", "--exec-path", "--html-path"):
            return True
        index += 2 if args[index] in GLOBAL_VALUE else 1
    return index >= len(args) or reads_only(args[index], args[index + 1:])


def segments(command: str) -> list[list[str]]:
    """Split a shell command into simple commands, dropping redirections."""
    result: list[list[str]] = []
    text = command.replace("\\\n", " ").replace("`", " ; ")
    for line in text.splitlines():
        lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        try:
            tokens = list(lexer)
        except ValueError:  # an unclosed quote, such as a multi-line message
            tokens = line.split()
        current: list[str] = []
        skip = False
        for token in tokens + [";"]:
            if skip:
                skip = False
            elif token and set(token) <= OPERATORS and ("<" in token or ">" in token):
                if current and current[-1].isdigit():
                    current.pop()  # a file descriptor, as in 2>/dev/null
                skip = True  # the redirection target
            elif token and set(token) <= OPERATORS:
                if current:
                    result.append(current)
                current = []
            else:
                current.append(token)
    return result


def git_calls(command: str, depth: int = 0) -> list[list[str]]:
    """Return the arguments of each git invocation found in a shell command."""
    calls: list[list[str]] = []
    if depth > 3:
        return calls
    for words in segments(command):
        for word in words:
            if "$(" in word:
                calls += git_calls(word.split("$(", 1)[1], depth + 1)
        calls += segment_calls(words, depth)
    return calls


def segment_calls(words: list[str], depth: int) -> list[list[str]]:
    """Return the git invocation in one simple command.

    Looks past shell keywords such as if, then, or do, variable assignments,
    and wrappers such as sudo or xargs.
    """
    wrapped = False
    for index, word in enumerate(words):
        name = os.path.basename(word)
        if name == "git":
            return [words[index + 1:]]
        if name == "eval":
            return git_calls(" ".join(words[index + 1:]), depth + 1)
        if name in SHELLS:
            rest = words[index + 1:]
            for position, arg in enumerate(rest[:-1]):
                if arg.startswith("-") and not arg.startswith("--") and "c" in arg[1:]:
                    return git_calls(rest[position + 1], depth + 1)
            return []
        if name in WRAPPERS:
            wrapped = True
        elif not wrapped and word not in KEYWORDS and not (
                "=" in word and word.split("=", 1)[0].isidentifier()):
            return []
    return []


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    tool_input = payload.get("tool_input") if isinstance(payload, dict) else None
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if isinstance(command, list):
        command = shlex.join(str(part) for part in command)
    if not isinstance(command, str) or "git" not in command:
        return
    held = [args for args in git_calls(command) if not git_allowed(args)]
    if not held:
        return
    shown = shlex.join(["git", *held[0]])
    shown = shown if len(shown) <= 60 else shown[:57] + "..."
    # Codex sets PLUGIN_ROOT and ignores "ask"; Claude Code sets CLAUDE_PROJECT_DIR.
    if os.environ.get("CLAUDE_PROJECT_DIR") and not os.environ.get("PLUGIN_ROOT"):
        decision = "ask"
        reason = (f"extension-modernization: `{shown}` changes the repository. "
                  "Approve it only if you asked for it.")
    else:
        decision = "deny"
        reason = (f"extension-modernization: `{shown}` changes the repository, and in CKAN "
                  "extension projects only the developer runs such git commands. Give the "
                  "developer the exact command to run instead.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": decision,
                                             "permissionDecisionReason": reason}}))


if __name__ == "__main__":
    main()
