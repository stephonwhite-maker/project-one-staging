#!/bin/bash
# Builds the shareable WordPress Playground bundle in playground/:
#   project-one.zip  the theme
#   p1-setup.zip     page content + setup script (unzipped to /p1 by the blueprint)
#   blueprint.json   the online blueprint (theme, import, login, open Home)
# Then commit and push; the share link reads these files from GitHub.
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$HERE/playground"
REPO="stephonwhite-maker/project-one-staging"
RAW="https://raw.githubusercontent.com/$REPO/main/playground"

python3 -I "$HERE/tools/build_content.py" >/dev/null
mkdir -p "$OUT"
rm -f "$OUT/project-one.zip" "$OUT/p1-setup.zip"
(cd "$HERE" && zip -qr -X "$OUT/project-one.zip" project-one -x '*.DS_Store')
(cd "$HERE" && zip -qr -X "$OUT/p1-setup.zip" content tools/setup.php -x '*.DS_Store')

cat > "$OUT/blueprint.json" <<JSON
{
	"\$schema": "https://playground.wordpress.net/blueprint-schema.json",
	"meta": { "title": "Project One Salon Suites (staging)", "author": "FORTHEWHEN" },
	"landingPage": "/",
	"preferredVersions": { "php": "8.3", "wp": "latest" },
	"features": { "networking": true },
	"login": false,
	"steps": [
		{ "step": "installTheme", "themeData": { "resource": "url", "url": "$RAW/project-one.zip?v=$(date +%s)" }, "options": { "activate": true } },
		{ "step": "unzip", "zipFile": { "resource": "url", "url": "$RAW/p1-setup.zip?v=$(date +%s)" }, "extractToPath": "/p1" },
		{ "step": "runPHP", "code": "<?php require '/wordpress/wp-load.php'; require '/p1/tools/setup.php';" }
	]
}
JSON

echo "Built $OUT"
echo "Share link: https://playground.wordpress.net/?mode=seamless&blueprint-url=$RAW/blueprint.json"
