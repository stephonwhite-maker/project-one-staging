"""Generate WordPress block markup for the five Project One pages.

Writes content/<slug>.html. Image tokens {{img:name}} and {{id:name}} are resolved by setup.php
when the pages are imported (they become Media Library URLs and attachment IDs).

Run: python3 tools/build_content.py
"""
import json, os, html

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
    roster = [
        ('stylist-latina-shag', 'Marisol Vega', 'Curly cuts and color', '4', 'Marisol', 'Marisol cuts curls dry, one at a time, and has eight years of regulars in The Grove. Book online or text the number on the suite door.'),
        ('stylist-barber-korean', 'Daniel Kim', 'Barber', '6', 'Daniel', 'Daniel does clean fades and classic scissor cuts, with a hot towel on every visit. Walk-ins welcome on Saturdays.'),
        ('stylist-lash-artist', 'Simone Reyes', 'Lashes and brows', '2', 'Simone', 'Simone does lash extensions, lifts and brow shaping in a calm window suite. Fills book up fast, so plan ahead.'),
        ('stylist-colorist-bob', 'Ingrid Larsen', 'Color specialist', '3', 'Ingrid', 'Ingrid specializes in soft blondes and lived-in color that grows out gracefully. Color consultations are free.'),
        ('stylist-mint-mullet', 'Jules Carter', 'Cuts and color', '5', 'Jules', 'Jules mixes bold color with shaggy, texture-first cuts. Bring a photo, leave with something better.'),
        ('hands-silver-hair', 'Renee Walker', 'Short cuts and gray blending', '3', 'Renee', 'Renee does precise short cuts and gray blending for clients who want to look like themselves, only sharper.'),
        ('beard-trim-90', 'Tasha Brooks', 'Barber and beard care', '6', 'Tasha', 'Tasha does barbering and beard care with a steady hand and a good playlist. Every age welcome in the chair.'),
    ]
    copy_slides = [
        group([
            group([h(3, name, 'h3'), p(f'{spec_}, Suite {suite}', 'eyebrow ink')], 'name-block'),
            p(bio),
            buttons([
                button(f'Book with {first}', '/location/', 'btn-outline'),
                button('All stylists', '/stylists/', 'btn-text underline'),
            ], 'btn-row'),
        ], 'slide' + (' is-active' if i == 0 else ''))
        for i, (photo, name, spec_, suite, first, bio) in enumerate(roster)
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

    return [hero, STRIPE, suites, space, indie(), stylists, voices, tour]


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
                info_cell('Open now', '1 suite'),
            ], 'info-row'),
        ], 'hero-main short'),
        group([img('interior-suite', 'fill')], 'hero-media short'),
    ], 'hero is-dark', 'section')

    def card(photo, name, num, desc, size, light, rate, ftype):
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
                buttons([button('Tour this suite', '/location/', 'btn-ink btn-block has-arrow')], 'card-cta'),
            ], 'card-body'),
        ], cls('suite-card', ftype), 'article')

    listing = group([
        group([
            h(2, 'Choose your suite', 'h1-text', 'list-h'),
            filter_bar('.suite-card', [('all', 'All'), ('window', 'Window'), ('interior', 'Interior'), ('available', 'Available now')]),
        ], 'list-head'),
        group([
            card('window-suite', 'Window suite', 1, 'Along the storefront. Natural light all day and your work on view from the street.', '140', 'Storefront windows', '$325', 'filter-window filter-available'),
            card('suite-cognac-chair', 'Interior suite', 2, 'Quiet and fully private, for color work and long appointments.', '120', 'Daylight LED panels', '$285', 'filter-interior filter-available'),
            card('blowdry', 'Studio suite', 3, 'Room for a second chair or a lash bed, for growing books.', '180', 'Corner windows', '$375', 'filter-window'),
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
            buttons([button('Download PDF', '#', 'btn-text underline has-arrow')], ''),
        ], 'list-head no-pad'),
        group([img('floor-plan-1500')], 'floor-plan'),
    ], 'plan section-pad', 'section')

    cta = group([cta_band('Book a tour', 'cta-h')], 'cta', 'section')
    return [hero, STRIPE, listing, included, lease, plan, cta]


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
                    buttons([button('Book with Marisol', '#', 'btn-ink')], ''),
                    p('01 / 03', 'eyebrow ink'),
                ], 'inline-row'),
            ], 'feature-copy'),
        ], 'feature-body pad-96'),
        slider_arrow('Next featured stylist', 'next'),
    ], 'slider sage rule-ink', 'section')

    people = [
        ('stylist-barber-korean', 'Daniel Kim', 'Barber', '6', 'filter-hair'),
        ('stylist-lash-artist', 'Simone Reyes', 'Lashes and brows', '2', 'filter-beauty'),
        ('stylist-colorist-bob', 'Ingrid Larsen', 'Color specialist', '3', 'filter-color'),
        ('stylist-mint-mullet', 'Jules Carter', 'Cuts and color', '5', 'filter-hair filter-color'),
        ('hands-silver-hair', 'Renee Walker', 'Short cuts and gray blending', '3', 'filter-hair filter-color'),
        ('beard-trim-90', 'Tasha Brooks', 'Barber and beard care', '6', 'filter-hair'),
    ]
    tints = ['blush', 'sage']

    def scard(i, photo, name, specialty, suite, ftype):
        return group([
            group([img(photo, 'fill')], f'card-media ratio-1-1 tint-{tints[i % 2]}'),
            group([h(3, name, 'h3'), p(f'Suite {suite}', 'num')], 'row-head'),
            p(specialty, 'eyebrow'),
            buttons([button('Book', '#', 'btn-text grow'), button('Instagram', '#', 'btn-text has-arrow')], 'card-links'),
        ], cls('stylist-card', ftype), 'article')

    directory = group([
        group([
            h(2, 'Directory', 'h1-text', 'dir-h'),
            filter_bar('.stylist-card', [('all', 'All'), ('hair', 'Hair'), ('color', 'Color'), ('beauty', 'Beauty')], 'blush-on'),
        ], 'list-head'),
        group([scard(i, *person) for i, person in enumerate(people)], 'stylist-grid'),
    ], 'listing', 'section')

    join = group([
        group([
            p('For stylists', 'eyebrow'),
            h(2, 'Your name could be here', 'join-title upper', 'join-h'),
            p('Ready for a suite of your own? Tour the building and see which rooms are open.', 'lede muted max-460'),
            buttons([button('Book a tour', '/location/', 'btn-paper'), button('See suites', '/suites/', 'btn-outline-light has-arrow')], 'btn-row'),
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
                info_cell('Address', '4127 Manchester Ave<br>St. Louis, MO 63110', buttons([button('Get directions', '#', 'btn-text underline')], 'tight')),
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


PAGES = {
    'home': ('Home', home),
    'suites': ('Suites', suites_page),
    'the-space': ('The Space', space_page),
    'stylists': ('Stylists', stylists_page),
    'location': ('Location and tours', location_page),
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for slug, (title, fn) in PAGES.items():
        body = '\n\n'.join(fn()) + '\n'
        assert '—' not in body, f'em dash in {slug}'
        with open(os.path.join(OUT, slug + '.html'), 'w', encoding='utf-8') as f:
            f.write(body)
        manifest.append({'slug': slug, 'title': title, 'file': slug + '.html', 'front': slug == 'home'})
    with open(os.path.join(OUT, 'pages.json'), 'w') as f:
        json.dump(manifest, f, indent=1)
    with open(os.path.join(OUT, 'alts.json'), 'w', encoding='utf-8') as f:
        json.dump(ALT, f, indent=1, ensure_ascii=False)
    print('wrote', [m['file'] for m in manifest])
