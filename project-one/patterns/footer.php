<?php
/**
 * Title: Site footer
 * Slug: project-one/footer
 * Categories: footer
 * Inserter: no
 */
?>
<!-- wp:html -->
<footer class="site-footer">
<div class="footer-brand">
<div class="footer-logo-row">
<img src="<?php echo esc_url( get_theme_file_uri( 'assets/logo/logo-stacked.svg' ) ); ?>" alt="Project One Salon Suites" width="62" height="120">
</div>
<p class="label-muted">2026 Project One</p>
</div>
<div class="footer-contact">
<div><p class="label-muted">Address</p><p>4127 Manchester Ave<br>St. Louis, MO 63110</p></div>
<div><p class="label-muted">Tel</p><p><a href="tel:+13145550142">(314) 555-0142</a></p></div>
<div><p class="label-muted">Email</p><p><a href="mailto:hello@projectonesalonsuites.com">hello@projectonesalonsuites.com</a></p></div>
</div>
<nav class="footer-links" aria-label="Footer">
<a href="<?php echo esc_url( home_url( '/suites/' ) ); ?>">Suites</a>
<a href="<?php echo esc_url( home_url( '/the-space/' ) ); ?>">The Space</a>
<a href="<?php echo esc_url( home_url( '/stylists/' ) ); ?>">Stylists</a>
<a href="<?php echo esc_url( home_url( '/location/' ) ); ?>">Location and tours</a>
<a href="<?php echo esc_url( home_url( '/lease/' ) ); ?>">Lease a suite</a>
</nav>
<nav class="footer-links" aria-label="Social">
<a href="#">Instagram</a>
<a href="#">TikTok</a>
<a href="#">Facebook</a>
<a href="<?php echo esc_url( home_url( '/privacy-policy/' ) ); ?>">Privacy policy</a>
<a href="<?php echo esc_url( home_url( '/accessibility/' ) ); ?>">Accessibility</a>
</nav>
</footer>
<!-- /wp:html -->
