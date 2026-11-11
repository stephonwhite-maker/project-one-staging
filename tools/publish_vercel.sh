#!/bin/bash
# Publish the WordPress site to Vercel as a static snapshot.
#   1. Make changes in WordPress (./start.sh, then http://localhost:9410/wp-admin)
#   2. Leave the local site running and run: ./tools/publish_vercel.sh
# Exports every page and asset (all motion, sliders, widgets) into ./vercel and deploys it to production.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
python3 -I "$HERE/tools/export_static.py"
cd "$HERE/vercel"
if [ ! -f .vercel/project.json ]; then
  npx -y vercel@latest link --yes --project project-one-salon-suites
fi
npx -y vercel@latest deploy --prod --yes
