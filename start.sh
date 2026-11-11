#!/bin/bash
# Project One Salon Suites: local WordPress staging (free, WordPress Playground CLI).
#
#   ./start.sh                 start the site at http://localhost:9410 (wp-admin: admin / password)
#   ./start.sh --reset-content re-import every page from content/ (overwrites edits made in WordPress)
#                              (or create an empty .reset-content file to do this once on the next start)
#
# First run downloads WordPress into ./site (kept local, ignored by Dropbox) and imports everything.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-9410}"
CLI="@wp-playground/cli@3.1.60"
SITE="$HERE/site"
mkdir -p "$SITE"
xattr -w com.dropbox.ignored 1 "$SITE" 2>/dev/null || true

# Regenerate page markup from tools/build_content.py.
python3 -I "$HERE/tools/build_content.py" >/dev/null

ARGS=(server
  --port="$PORT"
  --site-url="http://localhost:$PORT"
  --login
  --mount-dir-before-install "$SITE" /wordpress
  --mount-dir "$HERE/project-one" /wordpress/wp-content/themes/project-one
  --mount-dir "$HERE/content" /p1/content
  --mount-dir "$HERE/tools" /p1/tools
)

if [ ! -f "$SITE/wp-config.php" ]; then
  echo "First run: installing WordPress and importing the site..."
  ARGS+=(--blueprint="$HERE/blueprint.json")
elif [ "${1:-}" = "--reset-content" ] || [ -f "$HERE/.reset-content" ]; then
  rm -f "$HERE/.reset-content"
  echo "Re-importing pages from content/ ..."
  ARGS+=(--wordpress-install-mode=do-not-attempt-installing --blueprint="$HERE/blueprint.json")
else
  ARGS+=(--wordpress-install-mode=do-not-attempt-installing)
fi

exec npx -y "$CLI" "${ARGS[@]}"
