/*  GDPR Consent Banner — shows on first visit, remembers choice.
    Works with Google Consent Mode v2 (defaults set inline in <head>).
    Consent stored in localStorage as 'stv-consent'.                  */
(function () {
  var KEY = 'stv-consent';

  function getConsent() {
    try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; }
  }

  function setConsent(accepted) {
    var data = { accepted: accepted, date: new Date().toISOString() };
    try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {}

    if (accepted && typeof gtag === 'function') {
      gtag('consent', 'update', { 'analytics_storage': 'granted' });
    }
  }

  function hideBanner() {
    var el = document.getElementById('consent-banner');
    if (el) {
      el.style.opacity = '0';
      el.style.transform = 'translateY(100%)';
      setTimeout(function () { el.remove(); }, 300);
    }
  }

  function showBanner() {
    var banner = document.createElement('div');
    banner.id = 'consent-banner';
    banner.className = 'consent-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Cookie consent');
    banner.innerHTML =
      '<div class="consent-inner">' +
        '<p class="consent-text">' +
          'We use basic analytics to understand how visitors use this site. <strong>ZERO advertising tracking.</strong> ' +
          '<a href="/privacy.html">Privacy policy</a>' +
        '</p>' +
        '<div class="consent-buttons">' +
          '<button class="consent-btn consent-decline" id="consent-decline">Decline</button>' +
          '<button class="consent-btn consent-accept" id="consent-accept">Accept</button>' +
        '</div>' +
      '</div>';

    document.body.appendChild(banner);

    // Force reflow then animate in
    banner.offsetHeight;
    banner.style.opacity = '1';
    banner.style.transform = 'translateY(0)';

    document.getElementById('consent-accept').addEventListener('click', function () {
      setConsent(true);
      hideBanner();
    });

    document.getElementById('consent-decline').addEventListener('click', function () {
      setConsent(false);
      hideBanner();
    });
  }

  // "Manage cookies" footer link — resets consent and shows banner again
  document.addEventListener('click', function (e) {
    if (e.target && e.target.id === 'manage-cookies') {
      e.preventDefault();
      try { localStorage.removeItem(KEY); } catch (e) {}
      showBanner();
    }
  });

  // Show banner if no consent stored
  var existing = getConsent();
  if (!existing) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', showBanner);
    } else {
      showBanner();
    }
  }
}());
