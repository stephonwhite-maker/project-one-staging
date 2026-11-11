#!/bin/bash
# Builds the shareable WordPress Playground bundle in playground/:
#   project-one-<hash>.zip  the theme
#   p1-setup-<hash>.zip     page content + setup script (unzipped to /p1 by the blueprint)
#   blueprint.json   the online blueprint (theme, import, login, open Home)
# Then commit and push; the share link reads these files from GitHub.
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$HERE/playground"
REPO="stephonwhite-maker/project-one-staging"
RAW="https://raw.githubusercontent.com/$REPO/main/playground"

python3 -I "$HERE/tools/build_content.py" >/dev/null
mkdir -p "$OUT"
rm -f "$OUT"/*.zip
(cd "$HERE" && zip -qr -X "$OUT/theme.zip" project-one -x '*.DS_Store')
(cd "$HERE" && zip -qr -X "$OUT/setup.zip" content tools/setup.php -x '*.DS_Store')
# Content-hashed names: every change gets a new URL, so GitHub's 5-minute cache never serves an old zip.
THEME="project-one-$(shasum "$OUT/theme.zip" | cut -c1-10).zip"
SETUP="p1-setup-$(shasum "$OUT/setup.zip" | cut -c1-10).zip"
mv "$OUT/theme.zip" "$OUT/$THEME"
mv "$OUT/setup.zip" "$OUT/$SETUP"

cat > "$OUT/blueprint.json" <<JSON
{
	"\$schema": "https://playground.wordpress.net/blueprint-schema.json",
	"meta": { "title": "Project One Salon Suites (staging)", "author": "FORTHEWHEN" },
	"landingPage": "/",
	"preferredVersions": { "php": "8.3", "wp": "latest" },
	"features": { "networking": true },
	"login": false,
	"steps": [
		{ "step": "defineWpConfigConsts", "consts": { "P1_SHARED_STAGING": true } },
		{ "step": "installTheme", "themeData": { "resource": "url", "url": "$RAW/$THEME" }, "options": { "activate": true } },
		{ "step": "unzip", "zipFile": { "resource": "url", "url": "$RAW/$SETUP" }, "extractToPath": "/p1" },
		{ "step": "runPHP", "code": "<?php require '/wordpress/wp-load.php'; require '/p1/tools/setup.php';" }
	]
}
JSON

echo "Built $OUT"
echo "Share link: https://playground.wordpress.net/?mode=seamless&blueprint-url=$RAW/blueprint.json"
