#!/usr/bin/env bash
# BotForge installer.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash -s -- claude
#   curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash -s -- cursor ./my-project
#   bash install.sh --check           # self-test: dependencies + network + paths
#   bash install.sh --help
#
# Targets:
#   claude            Global Claude Code skill + commands → ~/.claude/
#   claude-project    Per-project → <project>/.claude/
#   cursor            Cursor MDC rule → <project>/.cursor/rules/
#   codex             AGENTS.md → <project>/AGENTS.md
#   system-prompt     Raw system prompt → <project>/botforge_system_prompt.txt

set -euo pipefail

REPO_URL="${BOTFORGE_REPO:-https://github.com/Zulut30/telegram-skills.git}"
REF="${BOTFORGE_REF:-main}"

color() { printf "\033[%sm%s\033[0m" "$1" "$2"; }
say()   { printf "$(color 36 '[BotForge]') %s\n" "$*"; }
ok()    { printf "$(color 32 '  ✓') %s\n" "$*"; }
warn()  { printf "$(color 33 '  ⚠') %s\n" "$*"; }
die()   { printf "$(color 31 '[BotForge] error:') %s\n" "$*" >&2; exit 1; }

print_help() {
  sed -n 's/^# //p; s/^#$//p' "$0" | head -20
  exit 0
}

run_check() {
  say "self-test (no installation performed)"
  command -v git >/dev/null 2>&1 && ok "git present" || die "git missing"
  command -v curl >/dev/null 2>&1 && ok "curl present" || warn "curl missing"
  command -v bash >/dev/null 2>&1 && ok "bash present" || die "bash missing"

  # writable HOME paths
  [[ -w "$HOME" ]] && ok "HOME writable ($HOME)" || warn "HOME not writable"

  # network reachability (no exit on failure)
  if curl -fsI --max-time 5 "$REPO_URL" >/dev/null 2>&1; then
    ok "repo reachable: $REPO_URL"
  else
    warn "repo unreachable (may work after clone)"
  fi

  say "self-test OK — ready to install"
  exit 0
}

# argument parsing
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then print_help; fi
if [[ "${1:-}" == "--check" ]]; then run_check; fi

TARGET="${1:-claude}"
PROJECT_DIR="${2:-.}"

command -v git >/dev/null 2>&1 || die "git is required"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

say "cloning $REPO_URL @ $REF"
git clone --depth 1 --branch "$REF" "$REPO_URL" "$TMPDIR" >/dev/null 2>&1 \
  || die "git clone failed"

install_claude_global() {
  local dest="${HOME}/.claude"
  mkdir -p "$dest/skills" "$dest/commands"

  # Warn about any existing BotForge / non-BotForge command files we would overwrite.
  for f in "$TMPDIR"/.claude/commands/*.md; do
    local name
    name="$(basename "$f")"
    if [[ -f "$dest/commands/$name" ]]; then
      warn "overwriting existing $dest/commands/$name"
    fi
  done
  if [[ -d "$dest/skills/botforge" ]]; then
    warn "overwriting existing $dest/skills/botforge"
  fi

  cp -r "$TMPDIR/.claude/skills/botforge" "$dest/skills/"
  # shellcheck disable=SC2046
  cp "$TMPDIR"/.claude/commands/*.md "$dest/commands/"
  ok "installed to $dest (global)"
}

install_claude_project() {
  [[ -d "$PROJECT_DIR" ]] || die "project dir not found: $PROJECT_DIR"
  mkdir -p "$PROJECT_DIR/.claude/skills" \
           "$PROJECT_DIR/.claude/commands" \
           "$PROJECT_DIR/.claude-plugin"
  cp -r "$TMPDIR/.claude/skills/botforge" "$PROJECT_DIR/.claude/skills/"
  # shellcheck disable=SC2046
  cp "$TMPDIR"/.claude/commands/*.md "$PROJECT_DIR/.claude/commands/"
  cp "$TMPDIR/.claude-plugin/plugin.json" "$PROJECT_DIR/.claude-plugin/"
  ok "installed to $PROJECT_DIR/.claude (per-project)"
}

install_cursor() {
  [[ -d "$PROJECT_DIR" ]] || die "project dir not found: $PROJECT_DIR"
  mkdir -p "$PROJECT_DIR/.cursor/rules"
  cp "$TMPDIR/cursor/.cursor/rules/botforge.mdc" "$PROJECT_DIR/.cursor/rules/"
  if [[ ! -f "$PROJECT_DIR/.cursorrules" ]]; then
    cp "$TMPDIR/cursor/.cursorrules" "$PROJECT_DIR/.cursorrules"
  fi
  ok "installed to $PROJECT_DIR/.cursor/rules/botforge.mdc"
}

install_codex() {
  [[ -d "$PROJECT_DIR" ]] || die "project dir not found: $PROJECT_DIR"
  if [[ -f "$PROJECT_DIR/AGENTS.md" ]]; then
    warn "$PROJECT_DIR/AGENTS.md exists — not overwriting"
  else
    cp "$TMPDIR/codex/AGENTS.md" "$PROJECT_DIR/AGENTS.md"
    ok "installed $PROJECT_DIR/AGENTS.md"
  fi
}

install_system_prompt() {
  [[ -d "$PROJECT_DIR" ]] || die "project dir not found: $PROJECT_DIR"
  cp "$TMPDIR/system_prompt.txt" "$PROJECT_DIR/botforge_system_prompt.txt"
  ok "copied raw system prompt to $PROJECT_DIR/botforge_system_prompt.txt"
}

case "$TARGET" in
  claude)         install_claude_global ;;
  claude-project) install_claude_project ;;
  cursor)         install_cursor ;;
  codex)          install_codex ;;
  system-prompt)  install_system_prompt ;;
  *)
    die "unknown target: $TARGET (see --help)"
    ;;
esac

say "done. next: /botforge-help (in Claude Code) or docs/QUICKSTART.md"
