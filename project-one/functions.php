<?php
/**
 * Project One Salon Suites theme.
 *
 * @package project-one
 */

defined( 'ABSPATH' ) || exit;

require_once __DIR__ . '/inc/tour-requests.php';
require_once __DIR__ . '/inc/lease-applications.php';
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
			$id     = get_queried_object_id();
			$parent = wp_get_post_parent_id( $id );
			if ( $parent ) {
				$classes[] = 'p1-page-' . sanitize_html_class( get_post_field( 'post_name', $parent ) ); // first, so the header highlights the section
			}
			$classes[] = 'p1-page-' . sanitize_html_class( get_post_field( 'post_name', $id ) );
		}
		return $classes;
	}
);

// Shared staging link (online blueprint defines P1_SHARED_STAGING): clean client view, no admin bar on the front end.
add_filter(
	'show_admin_bar',
	function ( $show ) {
		return defined( 'P1_SHARED_STAGING' ) && P1_SHARED_STAGING ? false : $show;
	}
);

/* ---- Search and AI answers: meta description, social preview tags, business schema, /llms.txt ---- */

add_action( 'init', function () { add_post_type_support( 'page', 'excerpt' ); } );

/** One line about the current page, from the page excerpt (set from content/pages.json on import). */
function project_one_description() {
	$desc = '';
	if ( is_singular() ) {
		$desc = get_post_field( 'post_excerpt', get_queried_object_id() );
	}
	if ( ! $desc ) {
		$desc = 'Private salon suites for rent in St. Louis, from $285 a week. Keep 100 percent of what you charge.';
	}
	return wp_strip_all_tags( $desc );
}

add_action(
	'wp_head',
	function () {
		$desc  = project_one_description();
		$title = wp_get_document_title();
		$url   = is_singular() ? get_permalink() : home_url( '/' );
		$image = get_theme_file_uri( 'assets/images/front-entry.webp' );
		echo '<meta name="description" content="' . esc_attr( $desc ) . '">' . "\n";
		echo '<meta property="og:type" content="website">' . "\n";
		echo '<meta property="og:site_name" content="Project One Salon Suites">' . "\n";
		echo '<meta property="og:title" content="' . esc_attr( $title ) . '">' . "\n";
		echo '<meta property="og:description" content="' . esc_attr( $desc ) . '">' . "\n";
		echo '<meta property="og:url" content="' . esc_url( $url ) . '">' . "\n";
		echo '<meta property="og:image" content="' . esc_url( $image ) . '">' . "\n";
		echo '<meta name="twitter:card" content="summary_large_image">' . "\n";

		$offer = function ( $name, $size, $price ) {
			return array(
				'@type'              => 'Offer',
				'name'               => $name . ', ' . $size . ' sq ft',
				'price'              => $price,
				'priceCurrency'      => 'USD',
				'priceSpecification' => array( '@type' => 'UnitPriceSpecification', 'price' => $price, 'priceCurrency' => 'USD', 'unitText' => 'week' ),
			);
		};
		$biz = array(
			'@context'                  => 'https://schema.org',
			'@type'                     => 'BeautySalon',
			'name'                      => 'Project One Salon Suites',
			'description'               => 'Private, lockable salon suites for licensed stylists, barbers, lash artists, estheticians and nail techs. Weekly rent, no commission.',
			'url'                       => home_url( '/' ),
			'telephone'                 => '+1-314-555-0142',
			'email'                     => 'hello@projectonesalonsuites.com',
			'image'                     => $image,
			'logo'                      => get_theme_file_uri( 'assets/logo/logo-stacked.svg' ),
			'priceRange'                => '$285 to $375 per week',
			'address'                   => array(
				'@type'           => 'PostalAddress',
				'streetAddress'   => '4127 Manchester Ave',
				'addressLocality' => 'St. Louis',
				'addressRegion'   => 'MO',
				'postalCode'      => '63110',
				'addressCountry'  => 'US',
			),
			'areaServed'                => 'St. Louis, Missouri',
			'openingHoursSpecification' => array(
				'@type'     => 'OpeningHoursSpecification',
				'dayOfWeek' => array( 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' ),
				'opens'     => '10:00',
				'closes'    => '18:00',
			),
			'makesOffer'                => array(
				$offer( 'Interior salon suite lease', 120, 285 ),
				$offer( 'Window salon suite lease', 140, 325 ),
				$offer( 'Studio salon suite lease', 180, 375 ),
			),
		);
		echo '<script type="application/ld+json">' . wp_json_encode( $biz, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ) . '</script>' . "\n";
	},
	5
);

/** /llms.txt: a plain summary for AI assistants (generated by tools/build_content.py). */
add_action(
	'parse_request',
	function () {
		$path = wp_parse_url( isset( $_SERVER['REQUEST_URI'] ) ? wp_unslash( $_SERVER['REQUEST_URI'] ) : '', PHP_URL_PATH ); // phpcs:ignore
		$home = wp_parse_url( home_url( '/' ), PHP_URL_PATH );
		if ( $path === rtrim( (string) $home, '/' ) . '/llms.txt' && is_readable( __DIR__ . '/llms.txt' ) ) {
			header( 'Content-Type: text/plain; charset=utf-8' );
			echo str_replace( '{{home}}', untrailingslashit( home_url() ), file_get_contents( __DIR__ . '/llms.txt' ) ); // phpcs:ignore
			exit;
		}
	}
);
