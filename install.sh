#!/usr/bin/env sh
# Install the production-ready-skill skills for Claude Code.
#   ./install.sh              -> ~/.claude/skills        (all your projects)
#   ./install.sh --project    -> ./.claude/skills        (current project only)
#   ./install.sh --uninstall  -> remove what this script installed
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
dest="${HOME}/.claude/skills"
mode=install
for a in "$@"; do
  case "$a" in
    --project) dest="$(pwd)/.claude/skills" ;;
    --uninstall) mode=uninstall ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done
if [ "$mode" = install ]; then
  command -v python3 >/dev/null 2>&1 || echo "warning: python3 not found; the helper scripts need Python 3.8+" >&2
  mkdir -p "$dest"
  for d in "$here"/skills/*/; do
    name="$(basename "$d")"
    rm -rf "${dest:?}/$name"
    cp -R "$d" "$dest/$name"
    echo "installed $name"
  done
  echo "Done. In Claude Code, open your project and run /launch"
else
  for d in "$here"/skills/*/; do
    name="$(basename "$d")"
    [ -d "$dest/$name" ] && rm -rf "${dest:?}/$name" && echo "removed $name"
  done
fi
