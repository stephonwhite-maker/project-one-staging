/* Project One: motion. Page veil transitions, scroll reveals, soft parallax.
   Off for prefers-reduced-motion and for the "Pause motion" accessibility option. */
(function () {
	'use strict';

	var root = document.documentElement;
	var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

	function paused() {
		if (reduce.matches) return true;
		try { return !!(JSON.parse(localStorage.getItem('p1-a11y') || '{}') || {}).motion; } catch (e) { return false; }
	}
	function motionOn() { return !paused() && !root.classList.contains('a11y-motion'); }

	/* ---------- page veil ---------- */
	var VEIL_OUT_MS = 1000; // time for the veil to cover the page before we navigate

	function lift() {
		if (!root.classList.contains('p1-entering')) return;
		requestAnimationFrame(function () {
			root.classList.add('p1-lift');
			setTimeout(function () {
				root.classList.remove('p1-entering', 'p1-lift');
				if ('scrollRestoration' in history) history.scrollRestoration = 'auto'; // back button keeps its place
			}, 1500);
		});
	}
	// Arriving: <head> may have set p1-entering. Start at the top, then lift once the first photo is ready (or after a short cap).
	if (root.classList.contains('p1-entering')) {
		if (!location.hash) {
			if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
			window.scrollTo({ top: 0, behavior: 'instant' });
		}
		var firstImg = document.querySelector('.page-content img');
		var lifted = false;
		var go = function () { if (!lifted) { lifted = true; lift(); } };
		if (firstImg && !firstImg.complete) {
			firstImg.addEventListener('load', go, { once: true });
			firstImg.addEventListener('error', go, { once: true });
			setTimeout(go, 700);
		} else {
			setTimeout(go, 120);
		}
	}

	function isInternal(a) {
		if (!a || !a.href || a.target === '_blank' || a.hasAttribute('download')) return false;
		var url;
		try { url = new URL(a.href, location.href); } catch (e) { return false; }
		if (url.origin !== location.origin) return false;
		if (/\/wp-(admin|login)/.test(url.pathname) || /\.(pdf|zip|webp|jpg|png)$/i.test(url.pathname)) return false;
		if (url.pathname === location.pathname && url.search === location.search) return false; // same page or #hash
		return true;
	}

	document.addEventListener('click', function (e) {
		if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
		var a = e.target.closest('a');
		if (!isInternal(a) || !motionOn()) return;
		e.preventDefault();
		try { sessionStorage.setItem('p1-veil', '1'); } catch (err) { /* storage blocked */ }
		root.classList.remove('p1-entering', 'p1-lift');
		root.classList.add('p1-leaving');
		setTimeout(function () { location.href = a.href; }, VEIL_OUT_MS);
	});

	// Back/forward cache: never come back to a covered page.
	window.addEventListener('pageshow', function (e) {
		if (e.persisted) root.classList.remove('p1-leaving', 'p1-entering', 'p1-lift');
	});

	if (!motionOn()) return;
	root.classList.add('p1-motion');

	/* ---------- scroll reveals ---------- */
	var content = document.querySelector('.page-content');
	if (!content) return;

	var marked = new Set();
	function mark(el, cls) {
		for (var p = el.parentElement; p; p = p.parentElement) { if (marked.has(p)) return; }
		marked.add(el);
		el.classList.add.apply(el.classList, cls.split(' '));
	}

	// Photos: curtain wipe. Left column wipes from the left, right column from the right.
	// A fully clipped figure never registers as visible, so we watch its frame and reveal the figure.
	var watchFor = new Map(); // observed element -> element that gets .is-in
	// Sliders move their own slides, so each stack reveals as one piece.
	content.querySelectorAll('.slides-copy').forEach(function (el) { mark(el, 'rv'); });
	content.querySelectorAll('.slides-media').forEach(function (el) { mark(el, 'rv rv-right'); });
	content.querySelectorAll('.wp-block-image').forEach(function (fig) {
		if (fig.closest('.slides-media')) return;
		watchFor.set(fig.parentElement, fig);
		var box = fig.closest('.hero-media, .split-media, .join-media');
		var dir = '';
		if (box) {
			var r = box.getBoundingClientRect();
			dir = r.left < window.innerWidth / 3 ? ' from-left' : ' from-right';
		}
		fig.classList.add('rv-img');
		if (dir) fig.classList.add(dir.trim());
		marked.add(fig);
	});
	// Frames and cards slide in from the side they sit on.
	content.querySelectorAll('.mat, .suite-card, .gallery-item, .stylist-card').forEach(function (el) {
		var r = el.getBoundingClientRect();
		mark(el, 'rv ' + (r.left + r.width / 2 < window.innerWidth / 2 ? 'rv-left' : 'rv-right'));
	});
	// Containers that should move as one piece.
	content.querySelectorAll('.cta-title, .cta-arrow, .info-cell, .spec-row, .filter-bar, .indie-panel, .faq-list details, .tour-form .field, .tour-form .submit-row, .wp-block-list li, .wp-block-buttons, .row-head, .suite-row, .floor-plan, .map-pin').forEach(function (el) { mark(el, 'rv'); });
	// Everything else that reads as text.
	content.querySelectorAll('.eyebrow, h1, h2, h3, p').forEach(function (el) { mark(el, 'rv'); });
	// Footer columns.
	document.querySelectorAll('.site-footer > *').forEach(function (el) { mark(el, 'rv'); });

	// Stagger siblings that arrive together: 90ms apart, soft cap.
	var entering = root.classList.contains('p1-entering');
	var io = new IntersectionObserver(function (entries) {
		var batch = entries.filter(function (en) { return en.isIntersecting; }).map(function (en) { return en.target; });
		batch.sort(function (a, b) {
			var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
			return (ra.top - rb.top) || (ra.left - rb.left);
		});
		batch.forEach(function (watched, i) {
			var base = entering ? 420 : 0; // let the veil lift first on arrival
			var el = watchFor.get(watched) || watched;
			el.style.setProperty('--d', (base + Math.min(i, 8) * 90) + 'ms');
			el.classList.add('is-in');
			// a frame can also be a revealed element in its own right (e.g. a matted photo)
			if (watchFor.has(watched) && marked.has(watched) && watched !== el) watched.classList.add('is-in');
			io.unobserve(watched);
		});
		entering = false;
	}, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
	marked.forEach(function (el) {
		if (el.classList.contains('rv-img')) return; // watched through its frame instead
		io.observe(el);
	});
	watchFor.forEach(function (fig, frame) { io.observe(frame); });

	/* ---------- soft parallax on large photos (eased, so it feels like silk, not a scroll-jack) ---------- */
	var layers = Array.prototype.slice.call(document.querySelectorAll('.hero-media img, .split-media img, .join-media img'))
		.map(function (img) { return { img: img, box: img.closest('.hero-media, .split-media, .join-media'), cur: 0 }; });
	if (layers.length) {
		var ticking = false;
		var frame = function () {
			var moving = false;
			var vh = window.innerHeight;
			layers.forEach(function (l) {
				var r = l.box.getBoundingClientRect();
				if (r.bottom < -100 || r.top > vh + 100) return;
				var progress = (r.top + r.height / 2 - vh / 2) / vh; // -1 .. 1 across the screen
				var target = Math.max(-1, Math.min(1, progress)) * -36;  // up to 36px of drift
				l.cur += (target - l.cur) * 0.08;
				if (Math.abs(target - l.cur) > 0.1) moving = true;
				l.img.style.setProperty('--py', l.cur.toFixed(2) + 'px');
			});
			if (moving && !root.classList.contains('a11y-motion')) { requestAnimationFrame(frame); } else { ticking = false; }
		};
		var kick = function () { if (!ticking) { ticking = true; requestAnimationFrame(frame); } };
		window.addEventListener('scroll', kick, { passive: true });
		window.addEventListener('resize', kick);
		kick();
	}

	// Pause motion toggled on mid-visit: show everything immediately.
	new MutationObserver(function () {
		if (root.classList.contains('a11y-motion')) {
			marked.forEach(function (el) { el.classList.add('is-in'); });
		}
	}).observe(root, { attributes: true, attributeFilter: ['class'] });
})();
