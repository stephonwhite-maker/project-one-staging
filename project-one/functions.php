<?php
/**
 * Project One Salon Suites theme.
 *
 * @package project-one
 */

defined( 'ABSPATH' ) || exit;

require_once __DIR__ . '/inc/tour-requests.php';
require_once __DIR__ . '/inc/widgets.php';

add_action(
	'after_setup_theme',
	function () {
		add_theme_support( 'wp-block-styles' );
		add_theme_support( 'editor-styles' );
		add_editor_style( 'assets/css/site.css' );
		remove_theme_support( 'core-block-patterns' );
	}
);

add_action(
	'wp_enqueue_scripts',
	function () {
		$ver = wp_get_theme()->get( 'Version' ) . '.' . filemtime( __DIR__ . '/assets/css/site.css' );
		wp_enqueue_style( 'project-one', get_theme_file_uri( 'assets/css/site.css' ), array(), $ver );
		wp_enqueue_script( 'project-one', get_theme_file_uri( 'assets/js/site.js' ), array(), filemtime( __DIR__ . '/assets/js/site.js' ), array( 'in_footer' => true, 'strategy' => 'defer' ) );
		wp_enqueue_style( 'project-one-motion', get_theme_file_uri( 'assets/css/motion.css' ), array( 'project-one' ), filemtime( __DIR__ . '/assets/css/motion.css' ) );
		wp_enqueue_script( 'project-one-motion', get_theme_file_uri( 'assets/js/motion.js' ), array(), filemtime( __DIR__ . '/assets/js/motion.js' ), array( 'in_footer' => true, 'strategy' => 'defer' ) );
	}
);

/**
 * Page veil: if the previous page started a veil transition, start this page covered
 * (set before first paint, so there is no flash), unless motion is reduced or paused.
 */
add_action(
	'wp_head',
	function () {
		?>
<script>
(function(){try{var d=document.documentElement;if(sessionStorage.getItem('p1-veil')!=='1')return;sessionStorage.removeItem('p1-veil');if(window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;var a=JSON.parse(localStorage.getItem('p1-a11y')||'{}')||{};if(a.motion)return;d.classList.add('p1-entering');setTimeout(function(){d.classList.remove('p1-entering','p1-lift');},4000);}catch(e){}})();
</script>
		<?php
	},
	1
);

add_action(
	'wp_body_open',
	function () {
		?>
<div class="p1-veil" aria-hidden="true"><span class="p1-veil-a"></span><span class="p1-veil-b"></span><img class="p1-veil-mark" src="<?php echo esc_url( get_theme_file_uri( 'assets/logo/logo-stacked.svg' ) ); ?>" alt="" width="56" height="108"></div>
		<?php
	}
);

/** Theme image URL, used by the CSS texture variables below. */
function project_one_img( $name ) {
	return get_theme_file_uri( 'assets/images/' . $name . '.webp' );
}

/** Spumoni textures and the testimonial photo are decorative, so they ride in as CSS variables. */
function project_one_texture_css() {
	$vars = array();
	foreach ( array( 'spumoni-stripes', 'spumoni-marble', 'spumoni-swirl', 'spumoni-scoop', 'spumoni-drips', 'barber-bw' ) as $name ) {
		$vars[] = '--img-' . $name . ': url(' . esc_url( project_one_img( $name ) ) . ');';
	}
	return ':root{' . implode( '', $vars ) . '}';
}
add_action(
	'wp_enqueue_scripts',
	function () {
		wp_add_inline_style( 'project-one', project_one_texture_css() );
	},
	20
);
add_action(
	'enqueue_block_assets',
	function () {
		if ( is_admin() ) {
			wp_register_style( 'project-one-editor-vars', false, array(), '1' );
			wp_enqueue_style( 'project-one-editor-vars' );
			wp_add_inline_style( 'project-one-editor-vars', project_one_texture_css() );
		}
	}
);

/** Body class per page slug, so the header can highlight the current page. */
add_filter(
	'body_class',
	function ( $classes ) {
		if ( is_front_page() ) {
			$classes[] = 'p1-page-home';
		} elseif ( is_page() ) {
			$classes[] = 'p1-page-' . sanitize_html_class( get_post_field( 'post_name', get_queried_object_id() ) );
		}
		return $classes;
	}
);

// Shared staging link (WordPress Playground online): clean client view, no admin bar on the front end.
add_filter(
	'show_admin_bar',
	function ( $show ) {
		return 'localhost' === wp_parse_url( home_url(), PHP_URL_HOST ) ? $show : false;
	}
);
