# Project One Salon Suites: WordPress staging

Free local WordPress copy of the Claude Design export, built as a custom block theme and run with WordPress Playground (no installs beyond Node).

## Start it

```bash
cd "$HOME/Library/CloudStorage/Dropbox/00_PROJECT ONE SALON SUITES/Website/wordpress" && ./start.sh
```

- Site: http://localhost:9410
- Admin: http://localhost:9410/wp-admin (local test login: admin / password)
- First run downloads WordPress into `site/` and imports everything (about a minute). Later runs reuse it, so edits made in WordPress stay.
- `./start.sh --reset-content` re-imports every page from `content/` and overwrites page edits made in WordPress.
- Port 9410 is used so it never clashes with the BGCSTL staging site on 9400.

## Live on Vercel

https://project-one-salon-suites.vercel.app

WordPress stays the place you edit. Vercel hosts a static snapshot of it (every page, photo, font, all motion, sliders, chat and accessibility panel).

To publish changes:
1. `./start.sh`, then edit at http://localhost:9410/wp-admin (or change the theme/content files)
2. With the local site still running: `./tools/publish_vercel.sh`

That re-exports the site into `vercel/` and deploys it to production. The tour form on Vercel shows a "preview site, requests not sent yet" message until it is connected to a form or email service.

## Share link (free, online)

https://playground.wordpress.net/?mode=seamless&blueprint-url=https://raw.githubusercontent.com/stephonwhite-maker/project-one-staging/main/playground/blueprint.json

- Runs the real WordPress site in the visitor's browser (WordPress Playground). Free, no expiry, your Mac does not need to be on.
- First load takes 10 to 20 seconds. Each visitor gets a fresh copy: edits and tour form submissions are not saved.
- To update it: `./tools/build_playground.sh`, then commit and push to GitHub (`stephonwhite-maker/project-one-staging`, public). GitHub caches files for about 5 minutes.

## What lives where

| Path | What it is |
|---|---|
| `project-one/` | The block theme: `theme.json`, templates, header/footer patterns, `assets/css/site.css`, `assets/js/site.js`, fonts, logos, images |
| `tools/build_content.py` | Generates the page block markup in `content/` (copy, image slots, alt text) |
| `tools/setup.php` | Activates the theme, imports photos into the Media Library, creates the pages, sets Home as the front page |
| `content/` | Generated page markup (do not hand edit, rerun the generator) |
| `site/` | The running WordPress install and database. Dropbox-ignored, so it stays on this Mac only |

## Notes

- Pages are built from core blocks (groups, headings, paragraphs, images, buttons, lists, details), so copy and photos are editable in the block editor. All 1,341 blocks across 15 pages validate.
- Spumoni textures and the testimonial photo are decorative theme CSS, not page content.
- Pages: Home, Suites, The Space, Stylists (plus 7 stylist profiles under /stylists/), Location, Lease a suite, Privacy policy, Accessibility statement. The stylist roster lives once in `STYLISTS` in `tools/build_content.py`.
- The tour form saves to wp-admin > Tour requests and the lease form (/lease/#apply) to wp-admin > Lease applications (no email yet).
- The floor plan PDF is `project-one/assets/docs/project-one-floor-plan.pdf`; rebuild it with `tools/floorplan/build.sh`.
- Instagram, TikTok and Facebook links stay as # until the real accounts exist.
- Accessibility panel options really apply (larger text, high contrast, underline links, readable spacing, pause motion) and are remembered per device.
- Motion lives in `assets/css/motion.css` and `assets/js/motion.js`: the page-to-page veil (blush then bone panels with the olive mark), soft scroll reveals, photo curtain wipes, gentle parallax, drifting spumoni textures and sliding hovers. All of it switches off for "reduce motion" devices and for the Pause motion option.
- The Home "Meet our stylists" slider cycles all seven stylists (arrows, swipe, arrow keys, slow autoplay that pauses on hover). In the editor each stylist is a "slide" group inside `slides-copy` (text) and `slides-media` (photo); keep the two in the same order.
- The Suites page floor plan is a mock 1,500 sq ft plan generated in Higgsfield (`floor-plan-1500.webp`).
- The map is still the design placeholder. The testimonial arrows are visual only until there is more than one quote, and the Stylists page featured block shows one stylist.
- Gosha Sans is bundled from the local font files. Confirm the web license before this goes live.
