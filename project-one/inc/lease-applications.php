<?php
/**
 * Lease application form: [p1_lease_form] shortcode, saved as private "Lease applications" in wp-admin.
 * Same look and handling as the tour form (nonce, honeypot, redirect back with a thank-you note).
 *
 * @package project-one
 */

defined( 'ABSPATH' ) || exit;

add_action(
	'init',
	function () {
		register_post_type(
			'p1_lease_app',
			array(
				'labels'          => array(
					'name'          => 'Lease applications',
					'singular_name' => 'Lease application',
					'menu_name'     => 'Lease applications',
				),
				'public'          => false,
				'show_ui'         => true,
				'show_in_menu'    => true,
				'menu_icon'       => 'dashicons-admin-network',
				'supports'        => array( 'title', 'editor' ),
				'capability_type' => 'post',
				'capabilities'    => array( 'create_posts' => 'do_not_allow' ),
				'map_meta_cap'    => true,
			)
		);
	}
);

function project_one_lease_fields() {
	return array(
		'name'    => 'Full name',
		'phone'   => 'Phone',
		'email'   => 'Email',
		'license' => 'License',
		'years'   => 'Years licensed',
		'now'     => 'Where you work now',
		'suite'   => 'Suite type',
		'term'    => 'Lease length',
		'start'   => 'Ideal start date',
		'link'    => 'Instagram or booking link',
		'note'    => 'Anything else',
	);
}

add_shortcode(
	'p1_lease_form',
	function () {
		$arrow = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 12 L12 4 M5 4 H12 V11"></path></svg>';
		$sent  = isset( $_GET['apply'] ) && 'sent' === $_GET['apply']; // phpcs:ignore WordPress.Security.NonceVerification
		ob_start();
		?>
<form class="tour-form lease-form" aria-label="Lease application" method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
<input type="hidden" name="action" value="p1_lease_app">
<?php wp_nonce_field( 'p1_lease_app', 'p1_lease_nonce' ); ?>
<div class="tour-hp" aria-hidden="true"><label for="l-company">Company</label><input id="l-company" type="text" name="company" tabindex="-1" autocomplete="off"></div>
<?php if ( $sent ) : ?>
<p class="tour-sent" role="status">Thanks for applying. We will be in touch within two business days to set up a tour.</p>
<?php endif; ?>
<div class="field"><label for="l-name">Full name</label><input id="l-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="l-phone">Phone</label><input id="l-phone" name="phone" type="tel" autocomplete="tel" required></div>
<div class="field"><label for="l-email">Email</label><input id="l-email" name="email" type="email" autocomplete="email" required></div>
<div class="field"><label for="l-license">License</label><select id="l-license" name="license"><option>Cosmetology</option><option>Barber</option><option>Esthetics</option><option>Other</option></select></div>
<div class="field"><label for="l-years">Years licensed</label><select id="l-years" name="years"><option>Less than 2</option><option>2 to 5</option><option>6 to 10</option><option>More than 10</option></select></div>
<div class="field"><label for="l-now">Where you work now</label><select id="l-now" name="now"><option>Renting a chair or booth</option><option>Commission salon</option><option>My own space</option><option>From home or mobile</option><option>Just getting started</option></select></div>
<div class="field"><label for="l-suite">Suite type</label><select id="l-suite" name="suite"><option>Window suite, $325 / week</option><option>Interior suite, $285 / week</option><option>Studio suite, $375 / week</option><option>Not sure yet</option></select></div>
<div class="field"><label for="l-term">Lease length</label><select id="l-term" name="term"><option>12 months</option><option>6 months</option></select></div>
<div class="field"><label for="l-start">Ideal start date</label><input id="l-start" name="start" type="date"></div>
<div class="field"><label for="l-link">Instagram or booking link (optional)</label><input id="l-link" name="link" type="text" inputmode="url"></div>
<div class="field field-wide"><label for="l-note">Anything else (optional)</label><textarea id="l-note" name="note" rows="3"></textarea></div>
<div class="field-wide submit-row"><button type="submit">Send application <?php echo $arrow; // phpcs:ignore ?></button></div>
</form>
		<?php
		return ob_get_clean();
	}
);

function project_one_handle_lease_app() {
	$back = wp_get_referer() ? wp_get_referer() : home_url( '/lease/' );
	$back = remove_query_arg( 'apply', strtok( $back, '#' ) );
	if ( ! isset( $_POST['p1_lease_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['p1_lease_nonce'] ) ), 'p1_lease_app' ) ) {
		wp_safe_redirect( $back );
		exit;
	}
	if ( empty( $_POST['company'] ) ) { // Honeypot: bots fill it and get a silent thank-you.
		$lines = array();
		foreach ( project_one_lease_fields() as $key => $label ) {
			$val     = isset( $_POST[ $key ] ) ? sanitize_textarea_field( wp_unslash( $_POST[ $key ] ) ) : '';
			$lines[] = $label . ': ' . $val;
		}
		$name = isset( $_POST['name'] ) ? sanitize_text_field( wp_unslash( $_POST['name'] ) ) : 'Unknown';
		wp_insert_post(
			array(
				'post_type'    => 'p1_lease_app',
				'post_status'  => 'private',
				'post_title'   => 'Lease application: ' . $name,
				'post_content' => implode( "\n", $lines ),
			)
		);
	}
	wp_safe_redirect( add_query_arg( 'apply', 'sent', $back ) . '#apply' );
	exit;
}
add_action( 'admin_post_nopriv_p1_lease_app', 'project_one_handle_lease_app' );
add_action( 'admin_post_p1_lease_app', 'project_one_handle_lease_app' );
