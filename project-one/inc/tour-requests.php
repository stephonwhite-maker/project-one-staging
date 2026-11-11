<?php
/**
 * Tour request form: [p1_tour_form] shortcode, saved as private "Tour requests" in wp-admin.
 *
 * @package project-one
 */

defined( 'ABSPATH' ) || exit;

add_action(
	'init',
	function () {
		register_post_type(
			'p1_tour_request',
			array(
				'labels'          => array(
					'name'          => 'Tour requests',
					'singular_name' => 'Tour request',
					'menu_name'     => 'Tour requests',
				),
				'public'          => false,
				'show_ui'         => true,
				'show_in_menu'    => true,
				'menu_icon'       => 'dashicons-calendar-alt',
				'supports'        => array( 'title', 'editor' ),
				'capability_type' => 'post',
				'capabilities'    => array( 'create_posts' => 'do_not_allow' ),
				'map_meta_cap'    => true,
			)
		);
	}
);

function project_one_tour_fields() {
	return array(
		'name'  => 'Full name',
		'phone' => 'Phone',
		'email' => 'Email',
		'work'  => 'What you do',
		'suite' => 'Suite interest',
		'date'  => 'Preferred day',
		'note'  => 'Anything else',
	);
}

add_shortcode(
	'p1_tour_form',
	function () {
		$arrow = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 12 L12 4 M5 4 H12 V11"></path></svg>';
		$sent  = isset( $_GET['tour'] ) && 'sent' === $_GET['tour']; // phpcs:ignore WordPress.Security.NonceVerification
		ob_start();
		?>
<form class="tour-form" aria-label="Tour request" method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
<input type="hidden" name="action" value="p1_tour_request">
<?php wp_nonce_field( 'p1_tour_request', 'p1_nonce' ); ?>
<div class="tour-hp" aria-hidden="true"><label for="t-company">Company</label><input id="t-company" type="text" name="company" tabindex="-1" autocomplete="off"></div>
<?php if ( $sent ) : ?>
<p class="tour-sent" role="status">Thanks. We got your request and will confirm a time by text or email.</p>
<?php endif; ?>
<div class="field"><label for="t-name">Full name</label><input id="t-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="t-phone">Phone</label><input id="t-phone" name="phone" type="tel" autocomplete="tel"></div>
<div class="field"><label for="t-email">Email</label><input id="t-email" name="email" type="email" autocomplete="email"></div>
<div class="field"><label for="t-work">What you do</label><select id="t-work" name="work"><option>Hair</option><option>Color</option><option>Barbering</option><option>Lashes and brows</option><option>Other</option></select></div>
<div class="field"><label for="t-suite">Suite interest</label><select id="t-suite" name="suite"><option>Window suite</option><option>Interior suite</option><option>Not sure yet</option></select></div>
<div class="field"><label for="t-date">Preferred day</label><input id="t-date" name="date" type="date"></div>
<div class="field field-wide"><label for="t-note">Anything else (optional)</label><textarea id="t-note" name="note" rows="3"></textarea></div>
<div class="field-wide submit-row"><button type="submit">Request a tour <?php echo $arrow; // phpcs:ignore ?></button></div>
</form>
		<?php
		return ob_get_clean();
	}
);

function project_one_handle_tour_request() {
	$back = wp_get_referer() ? wp_get_referer() : home_url( '/location/' );
	if ( ! isset( $_POST['p1_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['p1_nonce'] ) ), 'p1_tour_request' ) ) {
		wp_safe_redirect( $back );
		exit;
	}
	if ( ! empty( $_POST['company'] ) ) { // Honeypot.
		wp_safe_redirect( add_query_arg( 'tour', 'sent', $back ) . '#t-name' );
		exit;
	}
	$lines = array();
	foreach ( project_one_tour_fields() as $key => $label ) {
		$val     = isset( $_POST[ $key ] ) ? sanitize_textarea_field( wp_unslash( $_POST[ $key ] ) ) : '';
		$lines[] = $label . ': ' . $val;
	}
	$name = isset( $_POST['name'] ) ? sanitize_text_field( wp_unslash( $_POST['name'] ) ) : 'Unknown';
	wp_insert_post(
		array(
			'post_type'    => 'p1_tour_request',
			'post_status'  => 'private',
			'post_title'   => 'Tour request: ' . $name,
			'post_content' => implode( "\n", $lines ),
		)
	);
	wp_safe_redirect( add_query_arg( 'tour', 'sent', remove_query_arg( 'tour', $back ) ) . '#t-name' );
	exit;
}
add_action( 'admin_post_nopriv_p1_tour_request', 'project_one_handle_tour_request' );
add_action( 'admin_post_p1_tour_request', 'project_one_handle_tour_request' );
