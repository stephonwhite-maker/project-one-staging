<?php
/**
 * One-time (and re-runnable) site setup for the Project One staging site.
 * Runs inside WordPress via the Playground blueprint. Idempotent: pages are updated by slug,
 * images are imported once and reused.
 *
 * Expects: theme mounted at wp-content/themes/project-one, content at /p1/content.
 */

defined( 'ABSPATH' ) || exit;

require_once ABSPATH . 'wp-admin/includes/image.php';
require_once ABSPATH . 'wp-admin/includes/file.php';

$content_dir = '/p1/content';
$theme_dir   = WP_CONTENT_DIR . '/themes/project-one';

// Theme and basic settings.
switch_theme( 'project-one' );
update_option( 'blogname', 'Project One Salon Suites' );
update_option( 'blogdescription', 'Private salon suites for independent stylists in St. Louis' );
update_option( 'permalink_structure', '/%postname%/' );
update_option( 'default_comment_status', 'closed' );
update_option( 'timezone_string', 'America/Chicago' );
// Clean client view: no black admin bar on the front end (wp-admin still works).
foreach ( get_users( array( 'role' => 'administrator', 'fields' => 'ID' ) ) as $uid ) {
	update_user_meta( $uid, 'show_admin_bar_front', 'false' );
}

// Remove the default sample content.
foreach ( array( 'hello-world' => 'post', 'sample-page' => 'page' ) as $slug => $type ) {
	$p = get_page_by_path( $slug, OBJECT, $type );
	if ( $p ) {
		wp_delete_post( $p->ID, true );
	}
}
foreach ( get_posts( array( 'post_type' => 'page', 'post_status' => 'draft', 'name' => 'privacy-policy', 'numberposts' => 1 ) ) as $p ) {
	wp_delete_post( $p->ID, true );
}

// Alt text, written by tools/build_content.py so there is one source of truth.
$alts = json_decode( file_get_contents( $content_dir . '/alts.json' ), true );

/** Import one theme image into the Media Library (once). */
function p1_attachment( $name, $theme_dir, $alts ) {
	$existing = get_posts(
		array(
			'post_type'   => 'attachment',
			'post_status' => 'inherit',
			'meta_key'    => '_p1_source',
			'meta_value'  => $name,
			'numberposts' => 1,
		)
	);
	if ( $existing ) {
		return $existing[0]->ID;
	}
	$src     = $theme_dir . '/assets/images/' . $name . '.webp';
	$uploads = wp_upload_dir( '2026/11' );
	wp_mkdir_p( $uploads['path'] );
	$dest = $uploads['path'] . '/' . $name . '.webp';
	copy( $src, $dest );
	$id = wp_insert_attachment(
		array(
			'post_title'     => ucwords( str_replace( '-', ' ', $name ) ),
			'post_mime_type' => 'image/webp',
			'post_status'    => 'inherit',
		),
		$dest
	);
	$size = getimagesize( $dest );
	wp_update_attachment_metadata(
		$id,
		array(
			'width'  => $size[0],
			'height' => $size[1],
			'file'   => _wp_relative_upload_path( $dest ),
			'sizes'  => array(),
		)
	);
	update_post_meta( $id, '_p1_source', $name );
	if ( isset( $alts[ $name ] ) ) {
		update_post_meta( $id, '_wp_attachment_image_alt', $alts[ $name ] );
	}
	return $id;
}

// Pages. The import runs without a logged-in admin, so lift the HTML filter that would strip the inline arrow SVGs.
kses_remove_filters();
$pages    = json_decode( file_get_contents( $content_dir . '/pages.json' ), true );
$front_id = 0;
$report   = array();
foreach ( $pages as $i => $page ) {
	$body = file_get_contents( $content_dir . '/' . $page['file'] );
	$body = preg_replace_callback(
		'/\{\{(img|id):([a-z0-9-]+)\}\}/',
		function ( $mm ) use ( $theme_dir, $alts ) {
			$id = p1_attachment( $mm[2], $theme_dir, $alts );
			return 'id' === $mm[1] ? (string) $id : wp_get_attachment_url( $id );
		},
		$body
	);
	// Internal links: point at this site's home URL.
	$home = untrailingslashit( home_url() );
	$body = str_replace( array( 'href="/location/"', 'href="/suites/"', 'href="/the-space/"', 'href="/stylists/"' ), array( 'href="' . $home . '/location/"', 'href="' . $home . '/suites/"', 'href="' . $home . '/the-space/"', 'href="' . $home . '/stylists/"' ), $body );

	$existing = get_page_by_path( $page['slug'], OBJECT, 'page' );
	$args     = array(
		'post_type'    => 'page',
		'post_status'  => 'publish',
		'post_title'   => $page['title'],
		'post_name'    => $page['slug'],
		'post_content' => wp_slash( $body ),
		'menu_order'   => $i,
	);
	if ( $existing ) {
		$args['ID'] = $existing->ID;
		$id         = wp_update_post( $args );
	} else {
		$id = wp_insert_post( $args );
	}
	$report[] = $page['slug'] . '=' . $id;
	if ( ! empty( $page['front'] ) ) {
		$front_id = $id;
	}
}

update_option( 'show_on_front', 'page' );
update_option( 'page_on_front', $front_id );
flush_rewrite_rules();

echo 'Project One setup done: ' . implode( ', ', $report ) . "\n";
