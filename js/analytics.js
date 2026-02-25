/*  Comprehensive event tracking for GA4.
    Only fires events when consent is granted (Consent Mode v2 handles blocking).
    Loaded on all pages after consent.js.                                      */
(function () {
  function track(event, params) {
    if (typeof gtag === 'function') {
      try {
        var c = JSON.parse(localStorage.getItem('stv-consent'));
        if (c && c.accepted) gtag('event', event, params);
      } catch (e) {}
    }
  }

  var page = location.pathname;

  /* ── Scroll depth ── */
  var scrollMarks = { 25: false, 50: false, 75: false, 100: false };
  var ticking = false;

  function checkScroll() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (docHeight <= 0) return;
    var pct = Math.round((scrollTop / docHeight) * 100);

    for (var mark in scrollMarks) {
      if (!scrollMarks[mark] && pct >= parseInt(mark, 10)) {
        scrollMarks[mark] = true;
        track('page_scroll', { depth: mark + '%', page_path: page });
      }
    }
    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(checkScroll);
    }
  }, { passive: true });

  /* ── Time on page ── */
  var timeMarks = [30, 60, 120, 300];
  timeMarks.forEach(function (seconds) {
    setTimeout(function () {
      track('time_on_page', { seconds: seconds, page_path: page });
    }, seconds * 1000);
  });

  /* ── Click tracking (delegated) ── */
  document.addEventListener('click', function (e) {
    var link = e.target.closest('a');
    if (!link) {
      // Check for theme toggle
      var toggle = e.target.closest('.theme-toggle');
      if (toggle) {
        var theme = document.documentElement.getAttribute('data-theme');
        // After click, theme.js will have toggled it, so we read the NEW value
        setTimeout(function () {
          var newTheme = document.documentElement.getAttribute('data-theme');
          track('theme_toggle', { new_theme: newTheme });
        }, 50);
        return;
      }
      return;
    }

    var href = link.getAttribute('href') || '';
    var text = (link.textContent || '').trim().substring(0, 80);

    // Nav clicks
    if (link.closest('.nav-links') || link.closest('.nav-drawer')) {
      track('nav_click', { link_text: text, link_url: href, page_path: page });
      return;
    }

    // Language switcher
    if (link.classList.contains('lang-switcher-option')) {
      var lang = link.getAttribute('hreflang') || '';
      track('language_switch', { language: lang, page_path: page });
      return;
    }

    // Tool card clicks (homepage)
    if (link.classList.contains('tool-card-link')) {
      var toolName = '';
      var h3 = link.querySelector('h3');
      if (h3) toolName = h3.textContent.trim();
      track('tool_card_click', { tool_name: toolName, page_path: page });
      return;
    }

    // Outbound links
    if (href.indexOf('http') === 0 && link.hostname !== location.hostname) {
      track('outbound_click', { link_url: href, link_text: text, page_path: page });
      return;
    }

    // Internal links within article content
    if (link.closest('.content') && href.indexOf('#') !== 0) {
      track('internal_link', { link_url: href, link_text: text, page_path: page });
    }
  });

  /* ── Newsletter signup ── */
  document.addEventListener('submit', function (e) {
    var form = e.target.closest('.newsletter-form');
    if (form) {
      track('newsletter_signup', { page_path: page });
      return;
    }
    // Contact form
    if (e.target.closest('form[action*="formspree"]')) {
      track('contact_form_submit', { page_path: page });
    }
  });

  /* ── Calculator usage ── */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('button[type="submit"], .calc-btn, .compare-btn');
    if (!btn) return;
    var calcType = '';
    if (location.pathname.indexOf('fee-calculator') !== -1) calcType = 'fee_calculator';
    else if (location.pathname.indexOf('trade-comparison') !== -1) calcType = 'trade_comparison';
    else if (location.pathname.indexOf('roi-calculator') !== -1) calcType = 'roi_calculator';
    else if (location.pathname.indexOf('compare-platforms') !== -1) calcType = 'platform_comparison';
    if (calcType) {
      track('calculator_use', { calculator_type: calcType, page_path: page });
    }
  });

  /* ── 404 tracking ── */
  if (page === '/404.html' || document.title.indexOf('404') !== -1) {
    var attemptedUrl = location.href;
    var referrer = document.referrer || 'direct';
    track('404_hit', { attempted_url: attemptedUrl, referrer: referrer });
  }
}());
