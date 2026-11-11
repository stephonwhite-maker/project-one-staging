<?php
/**
 * Title: Site header
 * Slug: project-one/header
 * Categories: header
 * Inserter: no
 */
$p1_arrow = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 12 L12 4 M5 4 H12 V11"></path></svg>';
?>
<!-- wp:html -->
<header class="site-header">
<a class="site-logo" href="<?php echo esc_url( home_url( '/' ) ); ?>"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/logo/logo-wordmark.svg' ) ); ?>" alt="Project One Salon Suites, home" width="133" height="39"></a>
<nav class="site-nav" aria-label="Main">
<a href="<?php echo esc_url( home_url( '/suites/' ) ); ?>" data-nav="suites">Suites</a>
<a href="<?php echo esc_url( home_url( '/the-space/' ) ); ?>" data-nav="the-space">The Space</a>
<a href="<?php echo esc_url( home_url( '/stylists/' ) ); ?>" data-nav="stylists">Stylists</a>
<a href="<?php echo esc_url( home_url( '/location/' ) ); ?>" data-nav="location">Location</a>
<a class="nav-cta" href="<?php echo esc_url( home_url( '/location/' ) ); ?>">Book a tour <?php echo $p1_arrow; // phpcs:ignore ?></a>
</nav>
</header>
<!-- /wp:html -->
