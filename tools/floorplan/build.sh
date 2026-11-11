#!/bin/bash
# Rebuilds project-one/assets/docs/project-one-floor-plan.pdf from floorplan.html (headless Chrome).
set -euo pipefail
cd "$(dirname "$0")"
cp "../../../images/originals/floor-plan-1500.png" plan.png
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer --allow-file-access-from-files --print-to-pdf="../../project-one/assets/docs/project-one-floor-plan.pdf" "file://$PWD/floorplan.html" 2>/dev/null
rm -f plan.png
