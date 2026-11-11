<?php
/**
 * Accessibility panel (bottom left) and chat assistant (bottom right), printed on every page.
 *
 * @package project-one
 */

defined( 'ABSPATH' ) || exit;

add_action(
	'wp_footer',
	function () {
		$close = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 3 L13 13 M13 3 L3 13"></path></svg>';
		$arrow = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 12 L12 4 M5 4 H12 V11"></path></svg>';
		$opts  = array(
			'text'     => 'Larger text',
			'contrast' => 'High contrast',
			'links'    => 'Underline links',
			'spacing'  => 'Readable spacing',
			'motion'   => 'Pause motion',
		);
		?>
<div class="p1-widget p1-a11y" data-a11y>
<button type="button" class="p1-a11y-launch" aria-expanded="false" aria-controls="a11y-panel" aria-label="Accessibility options"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="4.5" r="1.8"></circle><path d="M4.5 8.5 L12 10 L19.5 8.5"></path><path d="M12 10 V14.5 L8.5 21"></path><path d="M12 14.5 L15.5 21"></path></svg></button>
<div id="a11y-panel" class="p1-panel" role="dialog" aria-labelledby="a11y-title" hidden>
<div class="p1-panel-head"><h2 id="a11y-title">Accessibility</h2><button type="button" class="p1-close" data-close aria-label="Close accessibility options"><?php echo $close; // phpcs:ignore ?></button></div>
		<?php foreach ( $opts as $key => $label ) : ?>
<button type="button" class="p1-opt" data-opt="<?php echo esc_attr( $key ); ?>" aria-pressed="false"><span><?php echo esc_html( $label ); ?></span><span class="p1-state">Off</span></button>
		<?php endforeach; ?>
<div class="p1-panel-foot"><button type="button" class="p1-reset" data-reset>Reset all</button><a href="<?php echo esc_url( home_url( '/accessibility/' ) ); ?>">Statement</a></div>
</div>
</div>

<div class="p1-widget p1-chat" data-chat>
<button type="button" class="p1-chat-launch" aria-expanded="false" aria-controls="chat-panel"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M3 4 H17 V14 H8 L4 17 V14 H3 Z"></path></svg><span data-chat-label>Ask us</span></button>
<div id="chat-panel" class="p1-panel p1-chat-panel" role="dialog" aria-labelledby="chat-title" hidden>
<div class="p1-chat-head"><div><h2 id="chat-title">Project One</h2><p>Leasing assistant. A person follows up on tours.</p></div><button type="button" class="p1-close" data-close aria-label="Close chat"><?php echo $close; // phpcs:ignore ?></button></div>
<div class="p1-chat-log" role="log" aria-live="polite">
<p class="msg msg-bot">Hi, I'm the Project One assistant. Looking for a suite? I can share rates, check what's open or set up a tour.</p>
<div class="p1-replies" data-replies>
<button type="button" data-reply="Book a tour">Book a tour</button>
<button type="button" data-reply="Suite rates">Suite rates</button>
<button type="button" data-reply="What is open">What is open</button>
<button type="button" data-reply="Talk to a person">Talk to a person</button>
</div>
</div>
<form class="p1-chat-form" data-chat-form><label for="chat-input" class="screen-reader-text">Type a message</label><input id="chat-input" type="text" placeholder="Type a message"><button type="submit" aria-label="Send message"><?php echo $arrow; // phpcs:ignore ?></button></form>
</div>
</div>
		<?php
	}
);
