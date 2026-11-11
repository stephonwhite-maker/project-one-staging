/* Project One Salon Suites: header state, filters, accessibility panel and chat assistant. */
(function () {
	'use strict';

	var root = document.documentElement;

	/* Header: mark the current page. */
	var bodyMatch = /p1-page-([\w-]+)/.exec(document.body.className);
	if (bodyMatch) {
		document.querySelectorAll('.site-nav a[data-nav="' + bodyMatch[1] + '"]').forEach(function (a) {
			a.setAttribute('aria-current', 'page');
		});
	}

	/* Filters: <div class="filter-bar" data-target=".selector"> with buttons data-filter="window|all".
	   Items opt in with a class like filter-window. If no item carries any filter class, everything stays visible. */
	document.querySelectorAll('.filter-bar').forEach(function (bar) {
		var items = document.querySelectorAll(bar.getAttribute('data-target'));
		var buttons = bar.querySelectorAll('button[data-filter]');
		buttons.forEach(function (btn) {
			btn.addEventListener('click', function () {
				var f = btn.getAttribute('data-filter');
				buttons.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
				var anyTagged = Array.prototype.some.call(items, function (el) { return /\bfilter-/.test(el.className); });
				var n = 0;
				items.forEach(function (el) {
					var show = f === 'all' || !anyTagged || el.classList.contains('filter-' + f);
					el.hidden = !show;
					el.classList.remove('is-filtering-in');
					if (show) {
						void el.offsetWidth; // restart the soft rise
						el.style.setProperty('--d', (n++ * 90) + 'ms');
						el.classList.add('is-filtering-in');
					}
				});
			});
		});
	});

	/* Sliders: .js-slider holds .slides-copy and .slides-media stacks that move together.
	   Arrows, swipe, arrow keys, a counter, and a slow autoplay that pauses on hover/focus and when motion is paused. */
	document.querySelectorAll('.js-slider').forEach(function (slider) {
		var stacks = Array.prototype.map.call(slider.querySelectorAll('.slides-copy, .slides-media'), function (st) {
			return Array.prototype.filter.call(st.children, function (c) { return c.classList.contains('slide'); });
		});
		var count = stacks.length ? stacks[0].length : 0;
		if (count < 2) return;
		var counter = slider.querySelector('.slide-count');
		var prev = slider.querySelector('.slider-prev');
		var next = slider.querySelector('.slider-next');
		var index = 0;
		var still = function () {
			return root.classList.contains('a11y-motion') || window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		};
		var pad = function (n) { return (n < 10 ? '0' : '') + n; };
		if (counter) counter.setAttribute('aria-live', 'polite');
		slider.setAttribute('aria-roledescription', 'carousel');

		function show(to, dir) {
			to = (to + count) % count;
			if (to === index) return;
			stacks.forEach(function (slides) {
				var out = slides[index], inn = slides[to];
				// incoming starts on the side it travels from, then glides home
				inn.style.transition = 'none';
				inn.style.transform = 'translateX(' + (dir * 56) + 'px)';
				void inn.offsetWidth;
				inn.style.transition = '';
				inn.style.transform = '';
				inn.classList.add('is-active');
				inn.removeAttribute('aria-hidden');
				inn.inert = false;
				out.classList.remove('is-active');
				out.style.transform = 'translateX(' + (-dir * 56) + 'px)';
				out.setAttribute('aria-hidden', 'true');
				out.inert = true;
			});
			index = to;
			if (counter) counter.textContent = pad(index + 1) + ' / ' + pad(count);
		}
		// start: hide everything but the first slide from assistive tech
		stacks.forEach(function (slides) {
			slides.forEach(function (sl, i) { if (i !== 0) { sl.setAttribute('aria-hidden', 'true'); sl.inert = true; } });
		});

		prev.addEventListener('click', function () { show(index - 1, -1); restart(); });
		next.addEventListener('click', function () { show(index + 1, 1); restart(); });
		slider.addEventListener('keydown', function (e) {
			if (e.key === 'ArrowLeft') { show(index - 1, -1); restart(); }
			if (e.key === 'ArrowRight') { show(index + 1, 1); restart(); }
		});

		// swipe
		var x0 = null;
		slider.addEventListener('pointerdown', function (e) { if (e.pointerType !== 'mouse') x0 = e.clientX; });
		slider.addEventListener('pointerup', function (e) {
			if (x0 === null) return;
			var dx = e.clientX - x0;
			x0 = null;
			if (Math.abs(dx) > 40) { show(index + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1); restart(); }
		});

		// slow autoplay
		var timer = null, hold = false;
		function restart() {
			clearInterval(timer);
			timer = setInterval(function () {
				if (!hold && !still() && !document.hidden) show(index + 1, 1);
			}, 6500);
		}
		slider.addEventListener('mouseenter', function () { hold = true; });
		slider.addEventListener('mouseleave', function () { hold = false; });
		slider.addEventListener('focusin', function () { hold = true; });
		slider.addEventListener('focusout', function () { hold = false; });
		restart();
	});

	/* Shared panel toggle for both widgets. */
	function wirePanel(widget, launcher, onToggle) {
		var panel = widget.querySelector('.p1-panel');
		var isOpen = false;
		var closeTimer;
		function set(open) {
			isOpen = open;
			clearTimeout(closeTimer);
			launcher.setAttribute('aria-expanded', open ? 'true' : 'false');
			if (open) {
				panel.hidden = false;
				// next frame, so the slide-up transition runs from the closed state
				requestAnimationFrame(function () { requestAnimationFrame(function () { panel.classList.add('is-open'); }); });
			} else {
				panel.classList.remove('is-open');
				var still = root.classList.contains('a11y-motion') || window.matchMedia('(prefers-reduced-motion: reduce)').matches;
				closeTimer = setTimeout(function () { if (!isOpen) panel.hidden = true; }, still ? 0 : 650);
			}
			if (onToggle) onToggle(open);
		}
		launcher.addEventListener('click', function () { set(!isOpen); });
		widget.querySelectorAll('[data-close]').forEach(function (b) {
			b.addEventListener('click', function () { set(false); launcher.focus(); });
		});
		widget.addEventListener('keydown', function (e) {
			if (e.key === 'Escape' && isOpen) { set(false); launcher.focus(); }
		});
	}

	/* Accessibility panel: each option toggles a class on <html> and is remembered on this device. */
	var a11y = document.querySelector('[data-a11y]');
	if (a11y) {
		var KEY = 'p1-a11y';
		var saved = {};
		try { saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { saved = {}; }
		var opts = a11y.querySelectorAll('[data-opt]');
		function apply() {
			opts.forEach(function (b) {
				var k = b.getAttribute('data-opt');
				var on = !!saved[k];
				root.classList.toggle('a11y-' + k, on);
				b.setAttribute('aria-pressed', on ? 'true' : 'false');
				b.querySelector('.p1-state').textContent = on ? 'On' : 'Off';
			});
			try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) { /* storage blocked */ }
		}
		opts.forEach(function (b) {
			b.addEventListener('click', function () {
				var k = b.getAttribute('data-opt');
				saved[k] = !saved[k];
				apply();
			});
		});
		a11y.querySelector('[data-reset]').addEventListener('click', function () { saved = {}; apply(); });
		wirePanel(a11y, a11y.querySelector('.p1-a11y-launch'));
		apply();
	}

	/* Chat assistant: scripted quick replies, same answers as the design. */
	var chat = document.querySelector('[data-chat]');
	if (chat) {
		var answers = {
			'Book a tour': 'Tours are by appointment. Tap Book a tour at the top of any page, or leave your name and number here and we will reach out.',
			'Suite rates': 'Window suites are $325 a week, interior suites $285 and studio suites $375. Rent covers utilities, Wi-Fi, laundry and weekly cleaning.',
			'What is open': 'Right now Suite 1 is open. It is a window suite right on the storefront. Want me to set up a tour so you can see it?',
			'Talk to a person': 'Sure. Leave your name and phone number and someone from Project One will call you back.'
		};
		var log = chat.querySelector('.p1-chat-log');
		var replies = chat.querySelector('[data-replies]');
		var label = chat.querySelector('[data-chat-label]');
		function say(text, who) {
			var p = document.createElement('p');
			p.className = 'msg msg-' + who;
			p.textContent = text;
			log.insertBefore(p, replies);
		}
		replies.querySelectorAll('[data-reply]').forEach(function (b) {
			b.addEventListener('click', function () {
				var q = b.getAttribute('data-reply');
				say(q, 'user');
				say(answers[q], 'bot');
			});
		});
		chat.querySelector('[data-chat-form]').addEventListener('submit', function (e) {
			e.preventDefault();
			var input = chat.querySelector('#chat-input');
			var text = input.value.trim();
			if (!text) return;
			say(text, 'user');
			say('Thanks. Leave your name and phone number and someone from Project One will follow up.', 'bot');
			input.value = '';
		});
		wirePanel(chat, chat.querySelector('.p1-chat-launch'), function (open) {
			label.textContent = open ? 'Close' : 'Ask us';
		});
	}
	/* Floor plan map: open suites only. The map moves inside the plan image so the hotspots line up at any size. */
	document.querySelectorAll('[data-plan-map]').forEach(function (map) {
		var wrap = map.closest('.floor-plan');
		var fig = wrap && wrap.querySelector('.wp-block-image');
		if (fig) fig.appendChild(map);
		var spots = map.querySelectorAll('.plan-spot');
		function close() {
			spots.forEach(function (s) { s.setAttribute('aria-expanded', 'false'); document.getElementById(s.getAttribute('aria-controls')).hidden = true; });
		}
		spots.forEach(function (spot) {
			var panel = document.getElementById(spot.getAttribute('aria-controls'));
			spot.addEventListener('click', function () {
				var open = spot.getAttribute('aria-expanded') === 'true';
				close();
				if (!open) {
					spot.setAttribute('aria-expanded', 'true');
					panel.hidden = false;
					panel.querySelector('.plan-apply').focus({ preventScroll: true });
					panel.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
				}
			});
			panel.querySelector('.plan-close').addEventListener('click', function () { close(); spot.focus(); });
			panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') { close(); spot.focus(); } });
		});
	});

	/* Suite vs chair vs commission calculator. Yearly take-home before product, taxes and insurance. */
	document.querySelectorAll('[data-calc]').forEach(function (calc) {
		var rent = +calc.dataset.rent, chair = +calc.dataset.chair, keep = +calc.dataset.keep, free = +calc.dataset.free || 0;
		var clients = calc.querySelector('#calc-clients'), ticket = calc.querySelector('#calc-ticket');
		var out = function (k) { return calc.querySelector('[data-out="' + k + '"]'); };
		var money = function (n) { return '$' + Math.round(n).toLocaleString('en-US'); };
		function update() {
			var gross = clients.value * ticket.value * 52;
			var c = gross * keep, ch = gross - chair * 52, su = gross - rent * (52 - free);
			calc.querySelector('#calc-clients-out').textContent = clients.value;
			calc.querySelector('#calc-ticket-out').textContent = money(ticket.value);
			out('commission').textContent = money(Math.max(0, c));
			out('chair').textContent = money(Math.max(0, ch));
			out('suite').textContent = money(Math.max(0, su));
			var vsC = su - c, vsChair = su - ch, note;
			note = vsC > 0 ? 'That is ' + money(vsC) + ' more a year than commission. ' : 'At this volume, commission keeps more in your pocket. A suite pays off as your book grows. ';
			note += vsChair >= 0
				? 'It also beats a chair by ' + money(vsChair) + ', with your own locked room, hours and retail shelf.'
				: 'Next to a chair it costs about ' + money(-vsChair / 52) + ' a week more, for your own locked room, hours and retail shelf.';
			out('note').textContent = note;
		}
		[clients, ticket].forEach(function (el) { el.addEventListener('input', update); });
		update();
	});

	/* Lease form: preselect the suite type from links like /lease/?suite=window&n=1#apply */
	(function () {
		var form = document.querySelector('.lease-form');
		if (!form) return;
		var q = new URLSearchParams(location.search), kind = q.get('suite'), n = q.get('n');
		var sel = form.querySelector('#l-suite');
		if (kind && sel) {
			Array.prototype.forEach.call(sel.options, function (o) { if (o.text.toLowerCase().indexOf(kind) === 0) sel.value = o.value || o.text; });
		}
		var note = form.querySelector('#l-note');
		if (n && note && !note.value) note.value = 'Interested in Suite ' + n.replace(/\D/g, '') + '.';
	})();
})();
