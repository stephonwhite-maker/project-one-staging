#!/usr/bin/env python3
"""Snapshot the running local WordPress site (./start.sh) into static files for Vercel.

    python3 tools/export_static.py            # writes ./vercel/

Crawls the five pages plus the 404 page, saves every same-site asset they use (CSS, JS, fonts,
images, logos), rewrites http://localhost:9410 to root-relative paths, and strips WordPress-only
bits (REST/oEmbed links, emoji script, admin bar). All theme motion and widgets are kept as is.
"""
import os
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("P1_LOCAL", "http://localhost:9410")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "vercel")
import json


def page_paths():
    """Every page from content/pages.json (front page is /, child pages sit under their parent)."""
    with open(os.path.join(HERE, "content", "pages.json")) as f:
        pages = json.load(f)
    out = []
    for pg in pages:
        if pg.get("front"):
            out.append("/")
        elif pg.get("parent"):
            out.append(f"/{pg['parent']}/{pg['slug']}/")
        else:
            out.append(f"/{pg['slug']}/")
    return out


PAGES = page_paths()

host = urllib.parse.urlparse(BASE).netloc
ORIGIN_RE = re.escape(BASE)
ORIGIN_JSON_RE = re.escape(BASE.replace("/", "\\/"))


def fetch(path):
    url = urllib.parse.urljoin(BASE, path)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read(), r.headers.get_content_type()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return e.read(), "text/html"
        raise


def local_path(url, ref_from="/"):
    """Return the site path (no query) for a same-site URL, else None."""
    url = url.strip().replace("\\/", "/").replace("&#038;", "&").replace("&amp;", "&")
    if not url or url.startswith(("data:", "#", "mailto:", "tel:", "javascript:")):
        return None
    full = urllib.parse.urljoin(urllib.parse.urljoin(BASE, ref_from), url)
    p = urllib.parse.urlparse(full)
    if p.netloc != host:
        return None
    return urllib.parse.unquote(p.path)


def save(path, data):
    dest = os.path.join(OUT, path.lstrip("/"))
    if path.endswith("/"):
        dest = os.path.join(dest, "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)


ASSET_EXT = re.compile(r"\.(css|js|woff2?|otf|ttf|svg|webp|png|jpe?g|gif|ico|json|pdf)$", re.I)
TOUR_NOTE = (
    "<script>document.querySelectorAll('form.tour-form, .tour-form form, form[action*=\"admin-post\"]').forEach(function(f){"
    "f.addEventListener('submit',function(e){e.preventDefault();var n=f.querySelector('.p1-static-note');"
    "if(!n){n=document.createElement('p');n.className='p1-static-note';n.setAttribute('role','status');"
    "n.style.cssText='margin:16px 0 0;font-size:14px;line-height:20px;color:#2a2523';f.appendChild(n);}"
    "n.textContent='Thanks. This is a preview site, so tour requests are not sent yet. Please call or email us to book a tour.';});});</script>"
)


def clean_html(html):
    # WordPress-only head links and scripts
    html = re.sub(r'<link[^>]+rel=["\'](?:https://api\.w\.org/|alternate|EditURI|shortlink|pingback|wlwmanifest)["\'][^>]*>\s*', "", html)
    html = re.sub(r'<link[^>]+rel=["\']dns-prefetch["\'][^>]*>\s*', "", html)
    # emoji detection and speculative prefetch rules are WordPress extras the static site does not need
    html = re.sub(r'<script\b[^>]*>(?:(?!</script>).)*?(?:wp-emoji|wpemoji|_wpemojiSettings)(?:(?!</script>).)*</script>\s*', "", html, flags=re.S)
    html = re.sub(r'<script[^>]*speculationrules[^>]*>.*?</script>\s*', "", html, flags=re.S)
    html = re.sub(r'<style[^>]*id=["\']wp-emoji-styles-inline-css["\'][^>]*>.*?</style>\s*', "", html, flags=re.S)
    html = re.sub(r'<link[^>]+href=["\'][^"\']*admin-bar[^"\']*["\'][^>]*>\s*', "", html)
    # same-site URLs become root-relative, and asset version queries go away
    html = re.sub(ORIGIN_JSON_RE, "", html)
    html = re.sub(ORIGIN_RE, "", html)
    html = re.sub(r'(/[^"\'\s()]+?\.(?:css|js|woff2?|otf|ttf|svg|webp|png|jpe?g))\?ver=[^"\'\s)&]+', r"\1", html)
    html = html.replace("</body>", TOUR_NOTE + "</body>", 1)
    return html


def main():
    try:
        fetch("/")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"Local site is not running at {BASE}. Start it with ./start.sh first. ({e})")

    # Fresh export each time, but keep Vercel's project link (.vercel/).
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):
        if name == ".vercel":
            continue
        target = os.path.join(OUT, name)
        shutil.rmtree(target) if os.path.isdir(target) else os.remove(target)

    assets, seen = set(), set()
    for page in PAGES + ["/p1-not-found-404/"]:
        data, _ = fetch(page)
        html = data.decode("utf-8")
        refs = re.findall(r'(?:src|href)=["\']([^"\']+)["\']', html)
        refs += [u for s in re.findall(r'srcset=["\']([^"\']+)["\']', html) for u in re.findall(r"(\S+)\s+\d+[wx]", s)]
        refs += re.findall(r'url\(["\']?([^"\')]+)["\']?\)', html)
        refs += re.findall(r'["\'](https?:\\?/\\?/[^"\']+)["\']', html)
        for r in refs:
            p = local_path(r, page)
            if p and ASSET_EXT.search(p) and "/wp-json/" not in p and "emoji" not in p:
                assets.add(p)
        cleaned = clean_html(html)
        if page.startswith("/p1-not-found"):
            save("/404.html", cleaned.encode("utf-8"))
        else:
            save(page, cleaned.encode("utf-8"))

    # Assets, following url() inside CSS (fonts, textures).
    queue = sorted(assets)
    while queue:
        p = queue.pop()
        if p in seen:
            continue
        seen.add(p)
        data, ctype = fetch(p)
        if p.endswith(".css"):
            css = data.decode("utf-8")
            for u in re.findall(r'url\(["\']?([^"\')]+)["\']?\)', css):
                lp = local_path(u, p)
                if lp and lp not in seen:
                    queue.append(lp)
            css = re.sub(ORIGIN_RE, "", css)
            data = css.encode("utf-8")
        elif p.endswith(".js"):
            data = re.sub(ORIGIN_RE.encode(), b"", data)
        save(p, data)

    with open(os.path.join(OUT, "vercel.json"), "w") as f:
        f.write('{\n\t"cleanUrls": true,\n\t"trailingSlash": true\n}\n')
    print(f"Exported {len(PAGES)} pages + 404 and {len(seen)} assets to {OUT}")


if __name__ == "__main__":
    main()
