"""Generate WordPress block markup for every Project One page (main pages, stylist profiles, lease, legal).

Writes content/<slug>.html. Image tokens {{img:name}} and {{id:name}} are resolved by setup.php
when the pages are imported (they become Media Library URLs and attachment IDs).

Run: python3 tools/build_content.py
"""
import json, os, html, re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'content')

ALT = {
    'hero-braids-window': 'Woman with long braids and a denim jacket seated by a sunlit salon window',
    'suite-cognac-chair': 'Empty salon suite with a cognac leather styling chair, a wall mirror and sheer curtains',
    'hands-silver-hair': 'Stylist cutting a smiling older client’s short silver hair beside a window',
    'stylist-latina-shag': 'Stylist with a curly shag and a black apron, arms crossed and smiling in her suite',
    'window-suite': 'Window suite with a white salon chair beside tall storefront windows and a yellow wall',
    'interior-suite': 'Quiet interior suite with a styling chair, a lamp, a round mirror and a cart of color bowls',
    'hallway-buzzcut': 'Bright hallway of suites where a stylist with a platinum buzz cut works on a smiling client',
    'front-entry': 'Brick storefront entry with a red salon sign and a potted plant beside the glass door',
    'lounge-grandma': 'Two women laughing together on the lounge sofa over coffee and pastries',
    'coily-texture': 'Close-up of hands parting short coily hair',
    'blowdry': 'Stylist blow drying a client’s long dark hair in warm side light',
    'stylist-barber-korean': 'Barber in a gray button-down smiling as he leans on a striped chair by the window',
    'stylist-lash-artist': 'Lash artist in a blue cardigan with her hair in a high bun, posing in her suite',
    'stylist-colorist-bob': 'Colorist with a silver bob and red glasses in front of shelves of product',
    'stylist-mint-mullet': 'Stylist with a mint green mullet and a graphic tee, smiling in her suite',
    'beard-trim-90': 'Stylist smiling as she trims an older man’s white beard',
    'hands-tools': 'Hands holding open shears and a comb against a cream drape',
    'floor-plan-1500': 'Floor plan of the 1,500 square foot building: window suites 1 and 2 on either side of the front entry and lobby, a central hall, interior suites 3 to 6 along the back, a shampoo and laundry room, a restroom and storage',
}

ARROW = '<svg width="{s}" height="{s}" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="{w}" aria-hidden="true"><path d="M4 12 L12 4 M5 4 H12 V11"></path></svg>'
LEFT = '<svg width="20" height="20" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M10 3 L5 8 L10 13"></path></svg>'
RIGHT = '<svg width="20" height="20" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M6 3 L11 8 L6 13"></path></svg>'


def attrs(d):
    d = {k: v for k, v in d.items() if v not in (None, '', {})}
    return (' ' + json.dumps(d, separators=(',', ':'), ensure_ascii=False)) if d else ''


def cls(*names):
    return ' '.join(n for n in names if n)


# ---- block helpers -------------------------------------------------------

def group(children, c=None, tag='div', anchor=None):
    a = attrs({'tagName': tag if tag != 'div' else None, 'className': c})
    idattr = f' id="{anchor}"' if anchor else ''
    inner = '\n\n'.join(children)
    return (f'<!-- wp:group{a} -->\n<{tag}{idattr} class="{cls("wp-block-group", c)}">{inner}</{tag}>\n<!-- /wp:group -->')


def p(text, c=None):
    a = attrs({'className': c})
    ca = f' class="{c}"' if c else ''
    return f'<!-- wp:paragraph{a} -->\n<p{ca}>{text}</p>\n<!-- /wp:paragraph -->'


def h(level, text, c=None, anchor=None):
    a = attrs({'level': level if level != 2 else None, 'className': c})
    idattr = f' id="{anchor}"' if anchor else ''
    return f'<!-- wp:heading{a} -->\n<h{level} class="{cls("wp-block-heading", c)}"{idattr}>{text}</h{level}>\n<!-- /wp:heading -->'


def img(name, c=None):
    a = attrs({'id': '__ID__', 'sizeSlug': 'full', 'linkDestination': 'none', 'className': c})
    a = a.replace('"__ID__"', '{{id:' + name + '}}')
    alt = html.escape(ALT[name], quote=True)
    return (f'<!-- wp:image{a} -->\n<figure class="{cls("wp-block-image size-full", c)}">'
            f'<img src="{{{{img:{name}}}}}" alt="{alt}" class="wp-image-{{{{id:{name}}}}}"/></figure>\n<!-- /wp:image -->')


def button(text, url, c=None):
    a = attrs({'className': c})
    return (f'<!-- wp:button{a} -->\n<div class="{cls("wp-block-button", c)}"><a class="wp-block-button__link wp-element-button" href="{url}">{text}</a></div>\n<!-- /wp:button -->')


def buttons(items, c=None):
    a = attrs({'className': c})
    return f'<!-- wp:buttons{a} -->\n<div class="{cls("wp-block-buttons", c)}">' + '\n\n'.join(items) + '</div>\n<!-- /wp:buttons -->'


def ul(items, c=None):
    a = attrs({'className': c})
    lis = '\n\n'.join(f'<!-- wp:list-item -->\n<li>{t}</li>\n<!-- /wp:list-item -->' for t in items)
    return f'<!-- wp:list{a} -->\n<ul class="{cls("wp-block-list", c)}">{lis}</ul>\n<!-- /wp:list -->'


def raw(markup):
    return f'<!-- wp:html -->\n{markup}\n<!-- /wp:html -->'


def shortcode(code):
    return f'<!-- wp:shortcode -->\n{code}\n<!-- /wp:shortcode -->'


def details(summary, answer, open_=False):
    a = attrs({'showContent': True if open_ else None})
    o = ' open' if open_ else ''
    return (f'<!-- wp:details{a} -->\n<details class="wp-block-details"{o}><summary>{summary}</summary>'
            f'{p(answer)}</details>\n<!-- /wp:details -->')


# ---- shared pieces --------------------------------------------------------

# One roster for every page. slug, photo, name, first, specialty, suite, filters, short bio,
# about (two paragraphs), services (name, price), hours.
STYLISTS = [
    dict(slug='marisol-vega', photo='stylist-latina-shag', name='Marisol Vega', first='Marisol', spec='Curly cuts and color', suite='4',
         filters='filter-hair filter-color',
         bio='Marisol cuts curls dry, one at a time, and has eight years of regulars in The Grove. Book online or text the number on the suite door.',
         about=['Marisol trained in curl-specific cutting after years of watching curly clients leave salons with hair that only looked right wet. Every cut starts dry, curl by curl, so you see the shape as it is being made.',
                'Her color work leans warm: copper, honey and soft dimension that stays kind to your curl pattern. Expect a long first visit, a lot of questions and a routine you can actually keep at home.'],
         services=[('Curly cut, dry', 'from $95'), ('Curl refresh and style', 'from $65'), ('Color, single process', 'from $110'), ('Dimensional color', 'from $165'), ('Curl consultation', 'Free')],
         hours='Tuesday to Saturday, 9am to 5pm'),
    dict(slug='daniel-kim', photo='stylist-barber-korean', name='Daniel Kim', first='Daniel', spec='Barber', suite='6',
         filters='filter-hair',
         bio='Daniel does clean fades and classic scissor cuts, with a hot towel on every visit. Walk-ins welcome on Saturdays.',
         about=['Daniel has been cutting for eleven years, starting in his uncle\'s shop and landing here when he wanted a quieter room and his own schedule.',
                'Fades, tapers and longer scissor cuts all get the same slow attention, and every visit ends with a hot towel. Saturdays are open for walk-ins until the chair fills up.'],
         services=[('Haircut', 'from $40'), ('Skin fade', 'from $45'), ('Haircut and beard', 'from $60'), ('Beard trim and line up', 'from $25'), ('Kids cut, 12 and under', 'from $30')],
         hours='Wednesday to Saturday, 10am to 7pm'),
    dict(slug='simone-reyes', photo='stylist-lash-artist', name='Simone Reyes', first='Simone', spec='Lashes and brows', suite='2',
         filters='filter-beauty',
         bio='Simone does lash extensions, lifts and brow shaping in a calm window suite. Fills book up fast, so plan ahead.',
         about=['Simone works out of a window suite with a lash bed, a heated blanket and a playlist quiet enough to fall asleep to. Plenty of her clients do.',
                'She keeps sets light and natural by default and builds up only if you ask. Brow shaping and tinting are matched to your face, not to a trend.'],
         services=[('Classic full set', 'from $140'), ('Hybrid full set', 'from $165'), ('Fill, 2 to 3 weeks', 'from $65'), ('Lash lift and tint', 'from $85'), ('Brow shape and tint', 'from $45')],
         hours='Monday to Friday, 10am to 6pm'),
    dict(slug='ingrid-larsen', photo='stylist-colorist-bob', name='Ingrid Larsen', first='Ingrid', spec='Color specialist', suite='3',
         filters='filter-color',
         bio='Ingrid specializes in soft blondes and lived-in color that grows out gracefully. Color consultations are free.',
         about=['Ingrid has spent fifteen years on color alone. Her specialty is blonde that looks expensive at week one and still looks intentional at week twelve.',
                'Every new client starts with a free consultation and a strand test, so the plan is honest about time, cost and how many visits it will take.'],
         services=[('Color consultation', 'Free'), ('Root touch up', 'from $85'), ('Partial highlight', 'from $150'), ('Full highlight or balayage', 'from $220'), ('Gloss and toner', 'from $55')],
         hours='Tuesday to Friday, 10am to 6pm'),
    dict(slug='jules-carter', photo='stylist-mint-mullet', name='Jules Carter', first='Jules', spec='Cuts and color', suite='5',
         filters='filter-hair filter-color',
         bio='Jules mixes bold color with shaggy, texture-first cuts. Bring a photo, leave with something better.',
         about=['Jules came up doing color at a busy downtown salon and moved into Suite 5 to slow down and do the work they actually love: shags, mullets and color that makes strangers ask questions.',
                'Bring a photo or bring nothing. Either way you will talk it through first, and you will leave with hair that fits how you live.'],
         services=[('Cut and style', 'from $70'), ('Shag or mullet cut', 'from $80'), ('Vivid color', 'from $150'), ('Color correction', 'by consultation'), ('Bang trim', '$15')],
         hours='Wednesday to Sunday, 11am to 7pm'),
    dict(slug='renee-walker', photo='hands-silver-hair', name='Renee Walker', first='Renee', spec='Short cuts and gray blending', suite='3',
         filters='filter-hair filter-color',
         bio='Renee does precise short cuts and gray blending for clients who want to look like themselves, only sharper.',
         about=['Renee shares Suite 3 and keeps her book small on purpose. Most of her clients have been with her for years, and many came to her ready to stop fighting their gray.',
                'Her short cuts are precise and easy to wear, and her gray blending is about softening the line, not hiding it.'],
         services=[('Short cut', 'from $60'), ('Gray blending', 'from $95'), ('Cut and blend', 'from $140'), ('Blow dry', 'from $45')],
         hours='Monday, Thursday and Saturday, 9am to 4pm'),
    dict(slug='tasha-brooks', photo='beard-trim-90', name='Tasha Brooks', first='Tasha', spec='Barber and beard care', suite='6',
         filters='filter-hair',
         bio='Tasha does barbering and beard care with a steady hand and a good playlist. Every age welcome in the chair.',
         about=['Tasha shares Suite 6 with Daniel and covers the early mornings and Sundays. Her chair sees first haircuts, wedding cuts and regulars in their nineties.',
                'Beard care is her favorite part of the job: shaping, hot towel and oil, done slowly enough to feel like the best part of your week.'],
         services=[('Haircut', 'from $40'), ('Beard shape and hot towel', 'from $35'), ('Haircut and beard', 'from $65'), ('Senior cut, 65 and up', 'from $30')],
         hours='Sunday to Wednesday, 8am to 4pm'),
]
BY_PHOTO = {st['photo']: st for st in STYLISTS}

# One list of suites for the floor plan map, the Suites page and the lease form.
# box = left, top, width, height in percent of the floor plan image. Only open suites are highlighted on the map,
# so leased suites never read as empty or "taken". Flip open to True when a suite frees up.
SUITE_TYPES = {
    'window': dict(label='Window suite', size='140', light='Storefront windows', rate='$325'),
    'interior': dict(label='Interior suite', size='120', light='Daylight LED panels', rate='$285'),
    'studio': dict(label='Studio suite', size='180', light='Corner windows', rate='$375'),
}
SUITES = [
    dict(n=1, kind='window', open=True, box=(6.3, 61.2, 24.2, 29.0)),
    dict(n=2, kind='window', open=False, box=(53.9, 61.2, 23.1, 29.0)),
    dict(n=3, kind='studio', open=False, box=(6.3, 12.6, 15.4, 31.0)),
    dict(n=4, kind='interior', open=False, box=(22.1, 12.6, 14.6, 31.0)),
    dict(n=5, kind='interior', open=False, box=(37.2, 12.6, 14.9, 31.0)),
    dict(n=6, kind='interior', open=False, box=(52.5, 12.6, 14.7, 31.0)),
]
OPEN = [s for s in SUITES if s['open']]
OPEN_KINDS = {s['kind'] for s in OPEN}


def open_count_text():
    n = len(OPEN)
    return 'Waitlist open' if n == 0 else f'{n} suite{"s" if n > 1 else ""} open'


def apply_url(kind=None, n=None):
    q = '&'.join(x for x in [f'suite={kind}' if kind else '', f'n={n}' if n else ''] if x)
    return '/lease/' + (f'?{q}' if q else '') + '#apply'


def plan_map():
    """Hotspots over the floor plan image: open suites only, each opens a small detail panel."""
    spots, panels = [], []
    for s in OPEN:
        t = SUITE_TYPES[s['kind']]
        l, tp, w, hgt = s['box']
        pid = f"plan-suite-{s['n']}"
        spots.append(
            f'<button type="button" class="plan-spot" style="left:{l}%;top:{tp}%;width:{w}%;height:{hgt}%" '
            f'aria-expanded="false" aria-controls="{pid}"><span class="plan-tag">Suite {s["n"]}, open</span></button>')
        panels.append(
            f'<div class="plan-panel" id="{pid}" hidden><p class="eyebrow">Suite {s["n"]}, open now</p>'
            f'<p class="plan-panel-title">{t["label"]}</p>'
            f'<dl><div><dt>Size</dt><dd>{t["size"]} sq ft</dd></div><div><dt>Light</dt><dd>{t["light"]}</dd></div>'
            f'<div><dt>Rate</dt><dd>From {t["rate"]} / week</dd></div></dl>'
            f'<a class="plan-apply" href="{apply_url(s["kind"], s["n"])}">Apply for Suite {s["n"]} {ARROW.format(s=14, w=1.5)}</a> '
            f'<button type="button" class="plan-close">Close</button></div>')
    legend = (f'<p class="plan-legend"><span class="plan-dot" aria-hidden="true"></span>{open_count_text()}. '
              'Tap a highlighted suite for details.</p>')
    return raw(f'<div class="plan-map" data-plan-map>{"".join(spots)}</div>{legend}{"".join(panels)}')


def profile_url(st, anchor=''):
    return f"/stylists/{st['slug']}/" + (f'#{anchor}' if anchor else '')


STRIPE = raw('<div class="spumoni-strip" aria-hidden="true"></div>')


def info_cell(label, value, extra=None):
    kids = [p(label, 'eyebrow'), p(value, 'small')]
    if extra:
        kids.append(extra)
    return group(kids, 'info-cell')


def spec(label, value, c=None):
    return group([p(label, 'spec-label'), p(value, cls('spec-value', c))], 'spec-row')


def cta_band(text, anchor, extra_class=None):
    """Big swirl band. The heading link stretches over the whole band."""
    return group([
        h(2, f'<a href="/location/">{text}</a>', 'cta-title upper', anchor),
        raw(f'<span class="cta-arrow" aria-hidden="true">{ARROW.format(s=96, w=0.8)}</span>'),
    ], cls('cta-band', extra_class))


def indie():
    return group([
        group([
            h(2, 'Built for independents', 'h1-text has-arrow', 'indie-h'),
            p('Project One is for the stylist who has outgrown a rented chair but isn\'t ready to sign for a whole storefront. You get a private room, your own lock and your own clientele. We handle the lease, the lights and the lobby.', 'lede'),
        ], 'indie-panel'),
    ], 'indie', 'section')


def slider_arrow(label, side, dark=False):
    icon = LEFT if side == 'prev' else RIGHT
    return raw(f'<button type="button" class="slider-arrow slider-{side}" aria-label="{label}">{icon}</button>')


def filter_bar(target, items, c=''):
    btns = ''.join(
        f'<button type="button" data-filter="{key}" aria-pressed="{"true" if i == 0 else "false"}">{label}</button>'
        for i, (key, label) in enumerate(items))
    return raw(f'<div class="filter-bar {c}" role="group" aria-label="Filter" data-target="{target}">{btns}</div>')


# ---- pages ----------------------------------------------------------------

def home():
    hero = group([
        group([
            group([
                p('(01) Salon suites, St. Louis', 'eyebrow'),
                h(1, 'A suite of your own.', 'hero-title'),
                p('Private, lockable salon suites for independent stylists and beauty pros. Your clients, your hours, your name on the door.', 'lede muted'),
                buttons([
                    button('Book a tour', '/location/', 'btn-paper'),
                    button('See suites', '/suites/', 'btn-outline-light has-arrow'),
                ], 'btn-row'),
            ], 'hero-copy'),
            group([
                info_cell('Location', '4127 Manchester Ave<br>St. Louis, MO'),
                info_cell('Leasing', '(314) 555-0142<br>hello@projectonesalonsuites.com'),
                info_cell('Access', 'Keyless entry.<br>Your own code.'),
            ], 'info-row'),
        ], 'hero-main'),
        group([img('hero-braids-window', 'fill')], 'hero-media'),
    ], 'hero is-dark', 'section')

    def suite_row(name, num, desc, rate, aria, ftype):
        return group([
            group([h(3, name, 'h3'), p(f'({num})', 'num')], 'row-head'),
            p(desc, 'small muted'),
            group([
                p(f'{rate} / week', 'rate'),
                raw(f'<a class="icon-link" href="/location/" aria-label="{aria}">{ARROW.format(s=16, w=1.5)}</a>'),
            ], 'row-foot'),
        ], cls('suite-row', ftype))

    suites = group([
        group([
            group([p('(02) Suites', 'eyebrow'), h(2, 'Pick your room', 'section-title upper', 'suites-h')], 'stack-20'),
            p('Every suite is private and locks with its own code. Bring your chair, your products and your book of clients. Rates are weekly, and tours are by appointment.', 'muted max-480'),
        ], 'section-intro'),
        filter_bar('.home-suites .suite-row', [('all', 'All suites'), ('window', 'Window'), ('interior', 'Interior')], 'on-dark'),
        group([
            group([
                suite_row('Window suite', 1, 'Along the storefront. Natural light all day and your work on view from the street. 140 sq ft.', '$325', 'Book a tour of a window suite', 'filter-window'),
                suite_row('Interior suite', 2, 'Quiet and fully private, for color work and long appointments. 120 sq ft.', '$285', 'Book a tour of an interior suite', 'filter-interior'),
                suite_row('Studio suite', 3, 'Room for a second chair or a lash bed, for growing books. 180 sq ft.', '$375', 'Book a tour of a studio suite', 'filter-window'),
                buttons([button('All suites and floor plan', '/suites/', 'btn-link-muted has-arrow')], 'row-link'),
            ], 'suite-list'),
            group([group([img('suite-cognac-chair', 'fill')], 'mat mat-bone ratio-4-3')], 'mat-cell'),
        ], 'suites-grid'),
    ], 'home-suites is-dark', 'section', 'suites')

    space = group([
        group([img('hands-silver-hair', 'fill')], 'split-media'),
        group([
            group([
                p('(03) The space', 'eyebrow'),
                h(2, 'You run your business. We run the building.', 'h1-text', 'space-h'),
                p('A restored 1920s storefront in The Grove, with tall windows, quiet halls and coffee on by 9. Walk in on a Tuesday morning and you will hear blow dryers, catch up in the lounge and get straight to work.', 'muted'),
            ], 'stack-24 max-520'),
            ul(['Keyless front entry with intercom', 'Smart lock and personal code on every suite', 'Window suites along the storefront', 'Common areas cleaned and restocked weekly'], 'num-list'),
            buttons([
                button('Explore the space', '/the-space/', 'btn-ink'),
                button('Instagram', '#', 'btn-text'),
                button('TikTok', '#', 'btn-text'),
                button('Facebook', '#', 'btn-text'),
            ], 'btn-row gap-32'),
        ], 'split-copy'),
    ], 'split', 'section', 'space')

    # Stylist slider: one copy slide and one photo slide per stylist, kept in step by site.js.
    roster = [(st['photo'], st['name'], st['spec'], st['suite'], st['first'], st['bio'], st) for st in STYLISTS]
    copy_slides = [
        group([
            group([h(3, name, 'h3'), p(f'{spec_}, Suite {suite}', 'eyebrow ink')], 'name-block'),
            p(bio),
            buttons([
                button(f'Book with {first}', profile_url(st, 'book'), 'btn-outline'),
                button('All stylists', '/stylists/', 'btn-text underline'),
            ], 'btn-row'),
        ], 'slide' + (' is-active' if i == 0 else ''))
        for i, (photo, name, spec_, suite, first, bio, st) in enumerate(roster)
    ]
    media_slides = [
        group([img(photo, 'fill')], 'slide mat mat-scoop ratio-1-1' + (' is-active' if i == 0 else ''))
        for i, (photo, *_rest) in enumerate(roster)
    ]
    stylists = group([
        slider_arrow('Previous stylist', 'prev'),
        group([
            group([
                p('(04) In the suites', 'eyebrow ink'),
                h(2, 'Meet our stylists', 'h1-text', 'stylists-h'),
                group(copy_slides, 'slides-copy'),
                p(f'01 / {len(roster):02d}', 'eyebrow ink slide-count'),
            ], 'feature-copy align-end'),
            group(media_slides, 'slides-media portrait-420 align-start'),
        ], 'feature-body'),
        slider_arrow('Next stylist', 'next'),
    ], 'slider sage js-slider', 'section', 'stylists')

    voices = group([
        slider_arrow('Previous quote', 'prev'),
        group([
            p('(05) From our tenants', 'eyebrow'),
            h(2, 'In their words', 'h2-text', 'voices-h'),
            p('“I went from renting a chair to running a business. My clients love the privacy, and I finally set my own hours.”', 'quote'),
            p('Jules Carter, Suite 5', 'eyebrow'),
            p('01 / 03', 'eyebrow'),
        ], 'voices-body'),
        slider_arrow('Next quote', 'next'),
    ], 'voices slider is-dark', 'section')

    tour = group([
        cta_band('Book a tour', 'tour-h', 'has-rule'),
        group([
            info_cell('Tours', 'By appointment, Tuesday to Saturday, 10am to 6pm'),
            info_cell('Call', '(314) 555-0142'),
            info_cell('Email', 'hello@projectonesalonsuites.com'),
        ], 'info-row info-row-light'),
    ], 'tour', 'section', 'tour')

    return [hero, STRIPE, suites, space, indie(), perk_band(), stylists, voices, tour]


def suites_page():
    hero = group([
        group([
            group([
                p('(02) Suites', 'eyebrow'),
                h(1, 'Suites', 'display-xl upper', 'page-h'),
                p('Private rooms with your own lock and code. Pick the light you work best in, move in your chair and products, and book clients on your own schedule.', 'lede muted max-460'),
            ], 'hero-copy'),
            group([
                info_cell('Rates', 'Weekly, from $285'),
                info_cell('Sizes', '120 to 180 sq ft'),
                info_cell('Open now', open_count_text()),
            ], 'info-row'),
        ], 'hero-main short'),
        group([img('interior-suite', 'fill')], 'hero-media short'),
    ], 'hero is-dark', 'section')

    def card(photo, kind, num, desc):
        t = SUITE_TYPES[kind]
        name, size, light, rate = t['label'], t['size'], t['light'], t['rate']
        ftype = f'filter-{"interior" if kind == "interior" else "window"}' + (' filter-available' if kind in OPEN_KINDS else '')
        cta = ('Apply for this suite', apply_url(kind)) if kind in OPEN_KINDS else ('Tour this suite', '/location/')
        return group([
            group([img(photo, 'fill')], 'card-media ratio-4-3'),
            group([
                group([h(3, name, 'h3'), p(f'({num})', 'num')], 'row-head'),
                p(desc, 'small muted'),
                group([
                    spec('Size', f'{size} sq ft'),
                    spec('Light', light),
                    spec('Rate', f'{rate} / week', 'big'),
                ], 'spec-list'),
                buttons([button(cta[0], cta[1], 'btn-ink btn-block has-arrow')], 'card-cta'),
            ], 'card-body'),
        ], cls('suite-card', ftype), 'article')

    listing = group([
        group([
            h(2, 'Choose your suite', 'h1-text', 'list-h'),
            filter_bar('.suite-card', [('all', 'All'), ('window', 'Window'), ('interior', 'Interior'), ('available', 'Available now')]),
        ], 'list-head'),
        group([
            card('window-suite', 'window', 1, 'Along the storefront. Natural light all day and your work on view from the street.'),
            card('suite-cognac-chair', 'interior', 2, 'Quiet and fully private, for color work and long appointments.'),
            card('blowdry', 'studio', 3, 'Room for a second chair or a lash bed, for growing books.'),
        ], 'card-grid'),
    ], 'listing', 'section')

    included = group([
        group([p('Included', 'eyebrow'), h(2, 'Every suite comes with', 'section-title upper', 'incl-h')], 'included-head'),
        ul(['Keyless front entry with intercom', 'A smart lock and your own personal code', 'Common areas cleaned and restocked weekly', 'Utilities and fast Wi-Fi'], 'included-list'),
    ], 'included is-dark', 'section')

    lease = group([
        group([
            p('Leasing', 'eyebrow'),
            h(2, 'How leasing works', 'h1-text', 'lease-h'),
            p('Tour the building, pick a suite, send your license and insurance, sign and get your code. Most stylists move in within a week.', 'muted'),
            buttons([button('Apply for a suite', '/lease/', 'btn-ink has-arrow')], 'btn-row'),
        ], 'stack-20 max-460'),
        group([
            spec('Lease term', '6 or 12 months'),
            spec('Deposit', 'One week of rent'),
            spec('Rent', 'Weekly, by auto-pay'),
            spec('Move in', 'December 1, 2026'),
        ], 'spec-list spec-lg'),
    ], 'two-col section-pad rule-bottom', 'section')

    plan = group([
        group([
            h(2, 'Floor plan', 'h1-text', 'plan-h'),
            buttons([button('Download PDF', '{{theme:assets/docs/project-one-floor-plan.pdf}}', 'btn-text underline has-arrow')], ''),
        ], 'list-head no-pad'),
        group([img('floor-plan-1500'), plan_map()], 'floor-plan has-map'),
    ], 'plan section-pad', 'section', 'floor-plan')

    cta = group([cta_band('Book a tour', 'cta-h')], 'cta', 'section')
    return [hero, STRIPE, listing, included, plan, perk_band(), lease, cta]


def space_page():
    hero = group([
        group([img('hallway-buzzcut', 'fill')], 'split-media short'),
        group([
            group([
                p('(03) The space', 'eyebrow'),
                h(1, 'The space', 'display-lg upper', 'page-h'),
                p('You run your business. We run the building. A restored 1920s storefront in The Grove, with tall windows, quiet halls and coffee on by 9.', 'lede muted max-460'),
            ], 'stack-28 max-560'),
            group([
                spec('Building', '1,500 sq ft'),
                spec('Suites', '6 private suites'),
                spec('Neighborhood', 'The Grove, St. Louis'),
            ], 'spec-list'),
        ], 'split-copy'),
    ], 'split rule-ink', 'section')

    def item(photo, caption, num, tint):
        return group([
            group([img(photo, 'fill')], f'card-media ratio-4-5 tint-{tint}'),
            group([p(caption), p(f'({num})', 'num')], 'gallery-caption'),
        ], 'gallery-item')

    gallery = group([
        group([h(2, 'Inside Project One', 'h1-text', 'gallery-h'), p('Gallery (6)', 'eyebrow')], 'list-head'),
        group([
            item('front-entry', 'Front entry', 1, 'blush'),
            item('window-suite', 'Window suites', 2, 'sage'),
            item('interior-suite', 'A suite', 3, 'blush'),
            item('beard-trim-90', 'In session', 4, 'sage'),
            item('lounge-grandma', 'Lounge', 5, 'blush'),
            item('coily-texture', 'Details', 6, 'sage'),
        ], 'gallery-grid'),
    ], 'listing', 'section')

    amen = group([
        group([
            p('Amenities', 'eyebrow'),
            h(2, 'Ready on day one', 'section-title upper', 'amen-h'),
            ul(['Keyless front entry with intercom', 'Smart lock and personal code on every suite', 'Window suites along the storefront', 'Common areas cleaned weekly', 'Snacks restocked every week', 'Washer and dryer on site'], 'num-list num-list-dark'),
        ], 'amen-copy'),
        group([group([img('blowdry', 'fill')], 'mat mat-bone ratio-4-5 portrait-560')], 'mat-cell'),
    ], 'amenities is-dark', 'section')

    cta = group([cta_band('See it in person', 'cta-h')], 'cta rule-ink', 'section')
    return [hero, STRIPE, gallery, indie(), amen, cta]


TINTS = ['blush', 'sage']


def stylist_card(i, st):
    return group([
        group([img(st['photo'], 'fill')], f'card-media ratio-1-1 tint-{TINTS[i % 2]}'),
        group([h(3, f'<a href="{profile_url(st)}">{st["name"]}</a>', 'h3'), p(f"Suite {st['suite']}", 'num')], 'row-head'),
        p(st['spec'], 'eyebrow'),
        buttons([button('Book', profile_url(st, 'book'), 'btn-text grow'), button('Profile', profile_url(st), 'btn-text has-arrow')], 'card-links'),
    ], cls('stylist-card', st['filters']), 'article')


def stylists_page():
    intro = group([
        group([p('(04) In the suites', 'eyebrow'), h(1, 'Stylists', 'display-xl upper', 'page-h')], 'stack-24'),
        p('Independent stylists and beauty pros, each running their own business under one roof. Book with them directly.', 'lede muted max-460'),
    ], 'page-intro', 'section')

    featured = group([
        slider_arrow('Previous featured stylist', 'prev'),
        group([
            group([img('stylist-latina-shag', 'fill')], 'mat mat-bone ratio-1-1 portrait-440 align-end'),
            group([
                p('Featured', 'eyebrow ink'),
                h(2, 'Marisol Vega', 'h1-text', 'feat-h'),
                p('Curly cuts and color, Suite 4', 'eyebrow ink rule-top'),
                p('Marisol cuts curls dry, one at a time, and has eight years of regulars in The Grove. Book online or text the number on the suite door.'),
                group([
                    buttons([button('Book with Marisol', '/stylists/marisol-vega/#book', 'btn-ink'), button('Profile', '/stylists/marisol-vega/', 'btn-text has-arrow')], ''),
                    p('01 / 03', 'eyebrow ink'),
                ], 'inline-row'),
            ], 'feature-copy'),
        ], 'feature-body pad-96'),
        slider_arrow('Next featured stylist', 'next'),
    ], 'slider sage rule-ink', 'section')

    directory = group([
        group([
            h(2, 'Directory', 'h1-text', 'dir-h'),
            filter_bar('.stylist-card', [('all', 'All'), ('hair', 'Hair'), ('color', 'Color'), ('beauty', 'Beauty')], 'blush-on'),
        ], 'list-head'),
        group([stylist_card(i, st) for i, st in enumerate(STYLISTS[1:])], 'stylist-grid'),
    ], 'listing', 'section')

    join = group([
        group([
            p('For stylists', 'eyebrow'),
            h(2, 'Your name could be here', 'join-title upper', 'join-h'),
            p('Ready for a suite of your own? Tour the building and see which rooms are open.', 'lede muted max-460'),
            buttons([button('Apply for a suite', '/lease/', 'btn-paper'), button('Book a tour', '/location/', 'btn-outline-light has-arrow')], 'btn-row'),
        ], 'join-copy'),
        group([img('hands-tools', 'fill')], 'join-media'),
    ], 'join is-dark', 'section')

    return [intro, STRIPE, featured, directory, join]


def location_page():
    hero = group([
        group([
            group([
                p('(05) Location and tours', 'eyebrow'),
                h(1, 'Book a tour', 'display-lg upper', 'page-h'),
                p('Tell us a little about your business and pick a day. We\'ll confirm a time by text or email.', 'lede muted max-440'),
            ], 'stack-24'),
            shortcode('[p1_tour_form]'),
        ], 'location-form'),
        group([
            raw('<div class="map-placeholder" role="img" aria-label="Map placeholder"><div class="map-pin"><span></span><p class="eyebrow ink">Project One</p><p class="small">Map: embed a muted, warm-toned map of the building and street.</p></div><div class="drips-strip" aria-hidden="true"></div></div>'),
            group([
                info_cell('Address', '4127 Manchester Ave<br>St. Louis, MO 63110', buttons([button('Get directions', 'https://www.google.com/maps/dir/?api=1&amp;destination=4127+Manchester+Ave+St.+Louis+MO+63110', 'btn-text underline')], 'tight')),
                info_cell('Tours', 'By appointment<br>Tuesday to Saturday, 10am to 6pm'),
                info_cell('Parking', 'Free lot behind the building, plus street parking on Manchester'),
            ], 'info-row info-row-light rule-ink-top'),
        ], 'location-map'),
    ], 'location-hero', 'section')

    faq = group([
        group([
            p('FAQ', 'eyebrow'),
            h(2, 'Good questions', 'section-title upper', 'faq-h'),
            p('Still wondering about something? Ask the chat in the corner or call (314) 555-0142.', 'muted max-360'),
        ], 'stack-20'),
        group([
            details('How long is a lease?', 'Leases run 6 or 12 months. After that you can renew month to month.', True),
            details('What does rent include?', 'Utilities, Wi-Fi, laundry, weekly cleaning of the common areas and snacks in the lounge.'),
            details('How do I get into the building?', 'Keyless entry. The front door has an intercom, and every suite has a smart lock with your own code.'),
            details('Can I bring my own products and equipment?', 'Yes. Bring your own chair, tools and product line. Every suite has a sink, outlets for two stations and locked storage.'),
            details('What licenses do I need?', 'A current Missouri cosmetology, barber or esthetics license, plus liability insurance. We ask for both before move in.'),
        ], 'faq-list'),
    ], 'two-col section-pad rule-ink', 'section')

    return [hero, STRIPE, faq]


def profile_page(st):
    first = st['first']
    hero = group([
        group([
            group([img(st['photo'], 'fill')], 'mat mat-scoop ratio-1-1 portrait-440 align-end'),
            group([
                p(f"(04) Stylists, Suite {st['suite']}", 'eyebrow ink'),
                h(1, st['name'], 'display-lg upper', 'page-h'),
                p(st['spec'], 'eyebrow ink rule-top'),
                p(st['bio'], 'lede'),
                buttons([
                    button(f'Book with {first}', '#book', 'btn-ink'),
                    button('All stylists', '/stylists/', 'btn-text underline'),
                ], 'btn-row'),
            ], 'feature-copy'),
        ], 'feature-body pad-96'),
    ], 'profile-hero sage rule-ink', 'section')

    about = group([
        group([
            p('About', 'eyebrow'),
            h(2, f'Meet {first}', 'h1-text', 'about-h'),
        ] + [p(t, 'muted') for t in st['about']], 'stack-20 max-520'),
        group([
            p('Services', 'eyebrow'),
            group([spec(name, price) for name, price in st['services']], 'spec-list spec-lg'),
            p('Prices are starting points. Final pricing depends on length, density and time.', 'small muted'),
        ], 'stack-20'),
    ], 'two-col section-pad rule-bottom', 'section')

    subject = html.escape(f'Booking with {st["name"]}').replace(' ', '%20')
    book = group([
        group([
            group([p('Booking', 'eyebrow'), h(2, f'Book with {first}', 'section-title upper', 'book-h')], 'stack-20'),
            p(f'Send a booking request through the front desk and {first} will reply within a day. Online booking goes live at move in.', 'muted max-480'),
        ], 'section-intro'),
        group([
            info_cell('Request a booking', f'<a href="mailto:hello@projectonesalonsuites.com?subject={subject}">Email the front desk</a>'),
            info_cell('Front desk', '<a href="tel:+13145550142">(314) 555-0142</a>'),
            info_cell('Hours', st['hours']),
            info_cell('Find them', f"Suite {st['suite']}, 4127 Manchester Ave"),
        ], 'info-row'),
    ], 'profile-book is-dark', 'section', 'book')

    others = [o for o in STYLISTS if o['slug'] != st['slug']]
    start = STYLISTS.index(st)
    picks = [others[(start + k) % len(others)] for k in range(3)]
    more = group([
        group([h(2, 'More stylists', 'h1-text', 'more-h'), buttons([button('All stylists', '/stylists/', 'btn-text underline has-arrow')], '')], 'list-head'),
        group([stylist_card(i, o) for i, o in enumerate(picks)], 'stylist-grid'),
    ], 'listing', 'section')
    return [hero, STRIPE, about, book, more]


PERK_TITLE = 'Half rent your first month'
PERK_TEXT = ('Then one rent-free week every year you stay, for a vacation, a class or a breath. '
             'Both are written into your lease, not a limited-time special.')


def perk_band(anchor='perk-h'):
    """Tenant perk with real terms. Placeholder terms until the owner confirms them."""
    return group([
        group([
            p('Tenant perk', 'eyebrow'),
            h(2, PERK_TITLE, 'section-title upper', anchor),
        ], 'stack-20'),
        group([
            p(PERK_TEXT, 'lede'),
            buttons([button('Apply for a suite', apply_url(), 'btn-ink has-arrow')], 'btn-row'),
        ], 'stack-20 max-480'),
    ], 'perk-band two-col section-pad blush', 'section')


def calculator():
    """Suite vs chair rent vs commission. Numbers are estimates, worked out in site.js."""
    return group([
        group([
            p('Run the numbers', 'eyebrow'),
            h(2, 'Suite vs chair vs commission', 'h1-text', 'calc-h'),
            p('Move the sliders to match your book. We compare what you keep in a year at a commission salon, renting a chair, and in an interior suite here.', 'muted'),
            p('Estimates before product, taxes and insurance, which you pay in every setup. Chair rent assumes $200 a week and commission assumes you keep 45 percent. The suite uses interior suite rent for your first year, with the tenant perk.', 'small muted'),
        ], 'stack-20 max-460'),
        raw('<div class="calc" data-calc data-rent="285" data-chair="200" data-keep="0.45" data-free="3">'
            '<div class="calc-field"><label for="calc-clients">Clients a week</label><output id="calc-clients-out" for="calc-clients">25</output>'
            '<input id="calc-clients" type="range" min="5" max="60" step="1" value="25"></div>'
            '<div class="calc-field"><label for="calc-ticket">Average ticket</label><output id="calc-ticket-out" for="calc-ticket">$85</output>'
            '<input id="calc-ticket" type="range" min="30" max="300" step="5" value="85"></div>'
            '<dl class="calc-results" aria-live="polite">'
            '<div><dt>Commission salon</dt><dd data-out="commission">$49,725</dd></div>'
            '<div><dt>Renting a chair</dt><dd data-out="chair">$100,100</dd></div>'
            '<div class="calc-win"><dt>Project One suite</dt><dd data-out="suite">$96,535</dd></div>'
            '</dl>'
            '<p class="calc-note" data-out="note">That is $46,810 more a year than commission. Next to a chair it costs about $69 a week more, for your own locked room, hours and retail shelf.</p>'
            '</div>'),
    ], 'two-col section-pad rule-bottom calc-section', 'section', 'calculator')


def lease_page():
    hero = group([
        group([
            group([
                p('(06) Leasing', 'eyebrow'),
                h(1, 'Lease a suite', 'display-lg upper', 'page-h'),
                p('Private, lockable suites for licensed stylists and beauty pros. Weekly rent, one lease, your name on the door.', 'lede muted max-460'),
                buttons([button('Apply now', '#apply', 'btn-paper'), button('See suites', '/suites/', 'btn-outline-light has-arrow')], 'btn-row'),
            ], 'hero-copy'),
            group([
                info_cell('Rent', 'Weekly, from $285'),
                info_cell('Lease', '6 or 12 months'),
                info_cell('Move in', 'December 1, 2026'),
            ], 'info-row'),
        ], 'hero-main short'),
        group([img('front-entry', 'fill')], 'hero-media short'),
    ], 'hero is-dark', 'section')

    why = group([
        group([img('coily-texture', 'fill')], 'split-media'),
        group([
            group([
                p('Why Project One', 'eyebrow'),
                h(2, 'Your business, your rules', 'h1-text', 'why-h'),
                p('Keep 100 percent of what you charge. Set your own hours, prices and product line. We take care of the building so you can take care of your clients.', 'muted'),
            ], 'stack-24 max-520'),
            ul(['Keep every dollar you charge, no commission', 'Your own lock, code and hours', 'Utilities, Wi-Fi and laundry included', 'Common areas cleaned and restocked weekly', 'A lounge your clients will want to sit in', 'Neighbors who refer clients, not compete for them'], 'num-list'),
        ], 'split-copy'),
    ], 'split', 'section')

    steps = group([
        group([p('How it works', 'eyebrow'), h(2, 'Four steps to your own suite', 'section-title upper', 'steps-h')], 'included-head'),
        ul(['Tour the building and see which suites are open', 'Pick your suite and your lease length', 'Send your license and liability insurance', 'Sign, get your code and move in'], 'included-list'),
    ], 'included lease-steps is-dark', 'section')

    rates = group([
        group([
            p('Suites and rates', 'eyebrow'),
            h(2, 'Three ways to work', 'h1-text', 'rates-h'),
            p('Every suite has a sink, outlets for two stations and locked storage. Rent is weekly by auto-pay, and your deposit is one week of rent.', 'muted'),
            buttons([button('Compare suites', '/suites/', 'btn-text underline has-arrow')], ''),
        ], 'stack-20 max-460'),
        group([
            spec('Window suite, 140 sq ft', '$325 / week'),
            spec('Interior suite, 120 sq ft', '$285 / week'),
            spec('Studio suite, 180 sq ft', '$375 / week'),
            spec('Deposit', 'One week of rent'),
            spec('Lease term', '6 or 12 months'),
        ], 'spec-list spec-lg'),
    ], 'two-col section-pad rule-bottom', 'section')

    apply_ = group([
        group([
            p('Apply', 'eyebrow'),
            h(2, 'Apply for a suite', 'section-title upper', 'apply-h'),
            p('It takes about five minutes. We reply within two business days to set up a tour.', 'muted max-440'),
            ul(['A current Missouri cosmetology, barber or esthetics license', 'Liability insurance, or a plan to get it before move in', 'An idea of when you want to start'], 'num-list'),
        ], 'stack-20 max-480'),
        shortcode('[p1_lease_form]'),
    ], 'two-col section-pad rule-ink lease-apply', 'section', 'apply')

    faq = group([
        group([p('FAQ', 'eyebrow'), h(2, 'Leasing questions', 'section-title upper', 'faq-h')], 'stack-20'),
        group([
            details('Can I share a suite?', 'Yes. Two stylists can share a studio suite on one lease, and each gets their own code.', True),
            details('Do you take a commission?', 'No. You pay rent and keep everything you charge, including retail.'),
            details('Can I sell my own retail products?', 'Yes. Your suite, your shelf, your product line.'),
            details('What happens at the end of my lease?', 'Renew for another term or go month to month. Give us 30 days notice if you are moving on.'),
        ], 'faq-list'),
    ], 'two-col section-pad rule-ink', 'section')

    cta = group([cta_band('See it in person', 'cta-h')], 'cta', 'section')
    who = group([
        group([p('Who it is for', 'eyebrow'), h(2, 'Suites by specialty', 'section-title upper', 'who-h')], 'stack-20'),
        group([
            group([h(3, f'<a href="/{pp["slug"]}/">{pp["short"]}</a>', 'h3'), p(pp['card'], 'small muted')], 'who-card')
            for pp in PROFESSIONS
        ], 'who-grid'),
    ], 'section-pad rule-bottom who', 'section')

    return [hero, STRIPE, why, calculator(), perk_band(), steps, rates, who, apply_, faq, cta]


PROFESSIONS = [
    dict(slug='hair-stylist-suites', short='Hair stylists', title='Suites for hair stylists', who='hair stylists',
         card='Cutters, colorists and curl specialists with a full book.',
         lede='Your own room for cuts, color and long appointments. Shampoo bowls down the hall, a sink in your suite and no one waiting for your chair.',
         fit='interior', match=lambda st: 'filter-hair' in st['filters'] and 'Barber' not in st['spec'] or 'filter-color' in st['filters'],
         points=['A sink in every suite, plus two shampoo bowls in the shared shampoo room', 'Outlets for two stations, so a dryer and an assistant both fit', 'Daylight LED panels in interior suites for true color', 'Washer and dryer on site for towels and capes', 'Keep 100 percent of your service and retail sales'],
         faq=[('Is there a shampoo bowl in my suite?', 'Every suite has a sink for color mixing and rinsing. Two full shampoo bowls sit in the shared shampoo room down the hall.'),
              ('Can I do color in an interior suite?', 'Yes. Interior suites have daylight LED panels, and most of our colorists choose them for the steady light.'),
              ('Can I bring an assistant?', 'Yes. Every suite has outlets for two stations, and the studio suite fits a second chair.')]),
    dict(slug='barber-suites', short='Barbers', title='Suites for barbers', who='barbers',
         card='Fades, beards and walk-in friendly hours on your terms.',
         lede='A private room with your own chair, your own music and your own hours. Early mornings, late nights and Sundays are all yours to book.',
         fit='window', match=lambda st: 'Barber' in st['spec'],
         points=['24/7 keyless entry, so early and late appointments work', 'Window suites put your chair on view from Manchester Ave', 'Outlets for clippers, trimmers and a second station', 'Lounge seating for the client who comes early', 'No commission and no one else setting your prices'],
         faq=[('Can I take walk-ins?', 'Yes. The lobby has seating, and you decide whether you take walk-ins or appointments only.'),
              ('What license do I need?', 'A current Missouri barber or cosmetology license, plus liability insurance before move in.'),
              ('Can I open on Sundays?', 'Yes. The building is open to tenants around the clock with your own code.')]),
    dict(slug='esthetician-suites', short='Lash, brow and skin', title='Suites for lash artists and estheticians', who='lash artists and estheticians',
         card='Lashes, brows, facials and waxing in a quiet, private room.',
         lede='A calm, closed-door room for lash sets, brows, facials and waxing. Dimmable light, a sink in the suite and space for a full treatment bed.',
         fit='studio', match=lambda st: 'filter-beauty' in st['filters'],
         points=['The studio suite fits a treatment bed with room to move around it', 'A closed door and private lock for clients who want quiet', 'A sink in every suite for hygiene and prep', 'Washer and dryer on site for linens', 'Set your own service menu and retail line'],
         faq=[('Will a lash or facial bed fit?', 'Yes. The 180 square foot studio suite fits a full treatment bed with room on both sides. Interior suites fit a compact bed.'),
              ('Can I control the lighting?', 'Yes. Suites have their own switches, and you are welcome to bring a lamp or ring light.'),
              ('What license do I need?', 'A current Missouri esthetics or cosmetology license, plus liability insurance before move in.')]),
    dict(slug='nail-tech-suites', short='Nail techs', title='Suites for nail techs', who='nail techs',
         card='Your own table, your own polish wall, your own clients.',
         lede='Room for a nail table, a pedicure chair and a polish wall, in a private suite where you set the menu and the music.',
         fit='interior', match=lambda st: 'filter-nails' in st['filters'],
         points=['Room for a nail table and a pedicure chair in a studio suite', 'Your own sink for prep and cleanup', 'Fresh air from the building system, plus room for your own extraction unit', 'Locked storage for polish and tools', 'Be the first nail tech in the building and pick up referrals from every other suite'],
         faq=[('Can I bring a pedicure chair?', 'Yes. A pedicure chair fits in the studio suite. Ask on your tour and we will measure it with you.'),
              ('Can I use an extraction fan?', 'Yes. Bring a tabletop extraction unit. Every suite has its own outlets.'),
              ('What license do I need?', 'A current Missouri cosmetology or manicurist license, plus liability insurance before move in.')]),
]


def profession_page(pp):
    t = SUITE_TYPES[pp['fit']]
    hero = group([
        group([
            group([
                p('(06) Leasing', 'eyebrow'),
                h(1, pp['title'], 'display-lg upper', 'page-h'),
                p(pp['lede'], 'lede muted max-460'),
                buttons([button('Apply now', apply_url(pp['fit']), 'btn-paper'), button('See open suites', '/suites/#floor-plan', 'btn-outline-light has-arrow')], 'btn-row'),
            ], 'hero-copy'),
            group([
                info_cell('Best fit', f"{t['label']}, {t['size']} sq ft"),
                info_cell('Rent', f"From {t['rate']} / week"),
                info_cell('Open now', open_count_text()),
            ], 'info-row'),
        ], 'hero-main short'),
        group([img('suite-cognac-chair' if pp['fit'] != 'window' else 'window-suite', 'fill')], 'hero-media short'),
    ], 'hero is-dark', 'section')

    fit = group([
        group([
            p('Why it works', 'eyebrow'),
            h(2, f"Built for {pp['who']}", 'h1-text', 'fit-h'),
            p('Every suite comes with utilities, Wi-Fi, laundry and weekly cleaning of the common areas. One weekly rent, no commission, no surprise fees.', 'muted'),
            buttons([button('Compare suites', '/suites/', 'btn-text underline has-arrow')], ''),
        ], 'stack-20 max-460'),
        ul(pp['points'], 'num-list'),
    ], 'two-col section-pad rule-bottom', 'section')

    team = [st for st in STYLISTS if pp['match'](st)]
    if team:
        neighbors = group([
            group([h(2, 'Already in the building', 'h1-text', 'team-h'), buttons([button('All stylists', '/stylists/', 'btn-text underline has-arrow')], '')], 'list-head'),
            group([stylist_card(i, st) for i, st in enumerate(team[:3])], 'stylist-grid'),
        ], 'listing', 'section')
    else:
        neighbors = group([
            group([
                p('Neighbors', 'eyebrow'),
                h(2, f"Be the first of the {pp['who']}", 'h1-text', 'team-h'),
                p('Every other suite here sends clients who ask where to get it done. Right now, nobody in the building does what you do.', 'muted'),
            ], 'stack-20 max-520'),
            buttons([button('Meet the stylists', '/stylists/', 'btn-text underline has-arrow')], ''),
        ], 'two-col section-pad rule-bottom', 'section')

    faq = group([
        group([p('FAQ', 'eyebrow'), h(2, 'Good questions', 'section-title upper', 'faq-h')], 'stack-20'),
        group([details(q, a, i == 0) for i, (q, a) in enumerate(pp['faq'])], 'faq-list'),
    ], 'two-col section-pad rule-ink', 'section')

    cta = group([cta_band('Book a tour', 'cta-h')], 'cta', 'section')
    return [hero, STRIPE, fit, neighbors, perk_band(), faq, cta]


def legal_page(eyebrow, title, intro, sections):
    head = group([
        group([p(eyebrow, 'eyebrow'), h(1, title, 'display-lg upper', 'page-h')], 'stack-24'),
        group([p(intro, 'lede muted'), p('Last updated November 11, 2026', 'eyebrow')], 'stack-20 max-460'),
    ], 'page-intro', 'section')
    rows = [group([h(2, t, 'h3'), group([p(x) for x in paras], 'legal-body')], 'legal-row') for t, paras in sections]
    return [head, STRIPE, group(rows, 'legal', 'section')]


def privacy_page():
    return legal_page('Privacy', 'Privacy policy',
        'What we collect when you use this site, why, and what you can ask us to do with it.',
        [
            ('What we collect', ['When you request a tour or apply for a suite, we collect what you type into the form: your name, phone, email, what you do and any notes.',
                                 'The chat in the corner answers from a short list of preset replies. What you type there is not saved or sent anywhere.']),
            ('How we use it', ['We use your details to reply to you, schedule tours and review lease applications. That is it.']),
            ('Who we share it with', ['We do not sell or rent your information. We only share it with the service providers that run this website and our email, and only so they can do that job.']),
            ('Cookies and settings', ['This site does not use advertising or tracking cookies.',
                                      'If you change a setting in the accessibility panel, your browser remembers it on your device so the site stays the way you like it. You can clear it any time with Reset all.']),
            ('How long we keep it', ['Tour requests are deleted after 12 months. Lease applications are kept for the length of a lease plus 3 years, or deleted after 12 months if you do not lease with us.']),
            ('Your choices', ['You can ask to see, correct or delete the information we have about you. Email hello@projectonesalonsuites.com or call (314) 555-0142.']),
            ('Children', ['This site is not meant for children under 13, and we do not knowingly collect their information.']),
            ('Changes', ['If we change this policy, we will update the date at the top of this page.']),
        ])


def accessibility_page():
    return legal_page('Accessibility', 'Accessibility statement',
        'We want everyone to be able to use this site and visit the building. Here is what we do and how to reach us if something gets in your way.',
        [
            ('Our goal', ['We aim to meet the Web Content Accessibility Guidelines (WCAG) 2.2 at level AA across this site.']),
            ('What we have done', ['Text and controls meet AA contrast. Every page works with a keyboard, with visible focus. Photos have text descriptions, and decorative textures are hidden from screen readers.',
                                   'The accessibility panel in the corner lets you turn on larger text, high contrast, underlined links and readable spacing, and pause all motion. If your device asks for reduced motion, we turn the animations off for you.']),
            ('Known limits', ['The map on the Location page is a placeholder for now. The address, tour hours and parking details are written out below it.',
                              'The floor plan is an image. The download and the image description list every room.']),
            ('Visiting the building', ['If you have questions about getting into the building or moving around it, call us before your tour and we will walk you through it.']),
            ('Tell us', ['If something on this site does not work for you, email hello@projectonesalonsuites.com or call (314) 555-0142. We reply within two business days.']),
        ])


PAGES = {
    'home': ('Home', home),
    'suites': ('Suites', suites_page),
    'the-space': ('The Space', space_page),
    'stylists': ('Stylists', stylists_page),
    'location': ('Location and tours', location_page),
    'lease': ('Lease a suite', lease_page),
    'privacy-policy': ('Privacy policy', privacy_page),
    'accessibility': ('Accessibility statement', accessibility_page),
}
for _pp in PROFESSIONS:
    PAGES[_pp['slug']] = (_pp['title'], (lambda pp: lambda: profession_page(pp))(_pp))
for _st in STYLISTS:
    PAGES[_st['slug']] = (_st['name'], (lambda st: lambda: profile_page(st))(_st), 'stylists')

# Meta descriptions (search results, link previews and AI answers). Under about 160 characters each.
DESC = {
    'home': 'Private salon suites for rent in St. Louis, from $285 a week. Keep 100 percent of what you charge. 4127 Manchester Ave, The Grove.',
    'suites': 'Window, interior and studio salon suites in St. Louis, 120 to 180 sq ft, from $285 a week. See the floor plan and which suites are open.',
    'the-space': 'Inside Project One Salon Suites: private suites, a client lounge, a shampoo room and laundry, in The Grove, St. Louis.',
    'stylists': 'Meet the independent stylists, barbers and lash artists at Project One Salon Suites in St. Louis, and book with them.',
    'location': 'Project One Salon Suites, 4127 Manchester Ave, St. Louis, MO 63110. Tours Tuesday to Saturday, 10am to 6pm, parking and directions.',
    'lease': 'Lease a salon suite in St. Louis: weekly rent from $285, 6 or 12 month leases, half rent your first month. Compare suite vs chair rent and apply.',
    'privacy-policy': 'How Project One Salon Suites collects and uses the information you send through this website.',
    'accessibility': 'Our accessibility commitment, WCAG 2.2 AA goal, and how to reach us if something on the site gets in your way.',
}
for _pp in PROFESSIONS:
    _t = SUITE_TYPES[_pp['fit']]
    DESC[_pp['slug']] = f"Salon suites for {_pp['who']} in St. Louis, from {_t['rate']} a week. Private room, your own hours, no commission. Half rent your first month."
for _st in STYLISTS:
    DESC[_st['slug']] = f"{_st['name']}, {_st['spec'].lower()}, Suite {_st['suite']} at Project One Salon Suites in The Grove, St. Louis. Services, prices and booking."

SITE = 'Project One Salon Suites'


def json_ld(data):
    return raw('<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>')


def faq_schema(body):
    pairs = re.findall(r'<summary>(.*?)</summary><!-- wp:paragraph -->\n<p>(.*?)</p>', body)
    if not pairs:
        return ''
    return json_ld({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': html.unescape(q), 'acceptedAnswer': {'@type': 'Answer', 'text': html.unescape(a)}} for q, a in pairs]})


def person_schema(st):
    return json_ld({'@context': 'https://schema.org', '@type': 'Person', 'name': st['name'], 'jobTitle': st['spec'],
                    'description': st['bio'], 'workLocation': {'@type': 'BeautySalon', 'name': SITE,
                    'address': {'@type': 'PostalAddress', 'streetAddress': f"4127 Manchester Ave, Suite {st['suite']}", 'addressLocality': 'St. Louis', 'addressRegion': 'MO', 'postalCode': '63110', 'addressCountry': 'US'}},
                    'makesOffer': [{'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': n}, 'description': pr} for n, pr in st['services']]})


def llms_txt():
    """Plain summary for AI assistants, served at /llms.txt. {{home}} becomes the site URL."""
    lines = [f'# {SITE}', '', '> Private, lockable salon suites for licensed beauty professionals at 4127 Manchester Ave, St. Louis, MO 63110 (The Grove). Weekly rent, no commission.', '',
             '## Key facts', '']
    for k, t in SUITE_TYPES.items():
        lines.append(f"- {t['label']}: {t['size']} sq ft, {t['light'][0].lower() + t['light'][1:]}, {t['rate']} per week")
    lines += ['- Lease: 6 or 12 months, deposit of one week of rent, rent by weekly auto-pay',
              f'- Tenant perk: {PERK_TITLE.lower()}, plus one rent-free week every year',
              '- Included: utilities, Wi-Fi, laundry, weekly cleaning of common areas, 24/7 keyless entry, a smart lock with your own code',
              f'- Availability: {open_count_text()}',
              '- Tours: by appointment, Tuesday to Saturday, 10am to 6pm. Phone (314) 555-0142, email hello@projectonesalonsuites.com', '',
              '## Pages', '']
    for slug, (title, *_rest) in PAGES.items():
        parent = _rest[1] if len(_rest) > 1 else None
        path = '/' if slug == 'home' else (f'/{parent}/{slug}/' if parent else f'/{slug}/')
        lines.append(f'- [{title}]({{{{home}}}}{path}): {DESC[slug]}')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for name in os.listdir(OUT):
        if name.endswith('.html'):
            os.remove(os.path.join(OUT, name))
    for slug, (title, fn, *parent) in PAGES.items():
        blocks = fn()
        if parent:
            blocks.append(person_schema(next(x for x in STYLISTS if x['slug'] == slug)))
        body = '\n\n'.join(blocks)
        body = '\n\n'.join(x for x in [body, faq_schema(body)] if x) + '\n'
        assert '—' not in body, f'em dash in {slug}'
        # Social buttons stay as # until the real accounts exist; anything else must go somewhere.
        assert not re.search(r'href="#">(?!Instagram|TikTok|Facebook)', body), f'dead link in {slug}'
        with open(os.path.join(OUT, slug + '.html'), 'w', encoding='utf-8') as f:
            f.write(body)
        assert len(DESC[slug]) <= 170, f'description too long for {slug}'
        entry = {'slug': slug, 'title': title, 'file': slug + '.html', 'front': slug == 'home', 'desc': DESC[slug]}
        if parent:
            entry['parent'] = parent[0]
        manifest.append(entry)
    with open(os.path.join(OUT, 'pages.json'), 'w') as f:
        json.dump(manifest, f, indent=1)
    with open(os.path.join(OUT, 'alts.json'), 'w', encoding='utf-8') as f:
        json.dump(ALT, f, indent=1, ensure_ascii=False)
    llms = llms_txt()
    assert '—' not in llms
    with open(os.path.join(OUT, '..', 'project-one', 'llms.txt'), 'w', encoding='utf-8') as f:
        f.write(llms)
    print('wrote', [m['file'] for m in manifest])
