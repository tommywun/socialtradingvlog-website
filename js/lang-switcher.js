(function () {
  var LANG_NAMES = {
    en: 'English',
    es: 'Español',
    de: 'Deutsch',
    fr: 'Français',
    pt: 'Português',
    ar: 'العربية'
  };

  // Read hreflang tags from <head>
  var links = document.querySelectorAll('link[rel="alternate"][hreflang]');
  if (!links.length) return;

  var langs = {};
  var currentLang = document.documentElement.lang || 'en';

  links.forEach(function (link) {
    var hl = link.getAttribute('hreflang');
    if (hl === 'x-default') return;
    langs[hl] = link.getAttribute('href');
  });

  // Need at least 2 languages to show a switcher
  if (Object.keys(langs).length < 2) return;

  // Build the switcher button + dropdown
  var wrapper = document.createElement('div');
  wrapper.className = 'lang-switcher';

  var btn = document.createElement('button');
  btn.className = 'lang-switcher-btn';
  btn.setAttribute('aria-label', 'Choose language');
  btn.setAttribute('aria-expanded', 'false');
  btn.innerHTML =
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
    '<circle cx="12" cy="12" r="10"/>' +
    '<line x1="2" y1="12" x2="22" y2="12"/>' +
    '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10A15.3 15.3 0 0 1 12 2z"/>' +
    '</svg>' +
    '<span class="lang-switcher-code">' + currentLang.toUpperCase() + '</span>';

  var dropdown = document.createElement('div');
  dropdown.className = 'lang-switcher-dropdown';

  // Sort: current language first, then alphabetical
  var sortedLangs = Object.keys(langs).sort(function (a, b) {
    if (a === currentLang) return -1;
    if (b === currentLang) return 1;
    return (LANG_NAMES[a] || a).localeCompare(LANG_NAMES[b] || b);
  });

  sortedLangs.forEach(function (code) {
    var a = document.createElement('a');
    a.href = langs[code];
    a.className = 'lang-switcher-option' + (code === currentLang ? ' lang-active' : '');
    a.setAttribute('hreflang', code);
    if (code === 'ar') a.setAttribute('dir', 'rtl');
    a.innerHTML =
      '<span class="lang-name">' + (LANG_NAMES[code] || code) + '</span>' +
      (code === currentLang ? '<span class="lang-check">&#10003;</span>' : '');
    dropdown.appendChild(a);
  });

  wrapper.appendChild(btn);
  wrapper.appendChild(dropdown);

  // Insert into desktop nav — before the CTA or hamburger
  var navInner = document.querySelector('.nav-inner');
  var navLinks = document.querySelector('.nav-links');
  if (navLinks) {
    // Insert as a <li> at the end of nav-links, before the CTA
    var li = document.createElement('li');
    li.style.position = 'relative';
    li.appendChild(wrapper);
    var ctaItem = navLinks.querySelector('.nav-cta');
    if (ctaItem && ctaItem.parentElement) {
      navLinks.insertBefore(li, ctaItem.parentElement);
    } else {
      navLinks.appendChild(li);
    }
  } else if (navInner) {
    navInner.appendChild(wrapper);
  }

  // Also add language links to mobile drawer
  var drawer = document.getElementById('nav-drawer');
  if (drawer) {
    var drawerUl = drawer.querySelector('ul');
    if (drawerUl) {
      var sep = document.createElement('li');
      sep.className = 'lang-drawer-sep';
      sep.innerHTML = '<span>Language</span>';
      drawerUl.appendChild(sep);

      sortedLangs.forEach(function (code) {
        if (code === currentLang) return;
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = langs[code];
        a.setAttribute('hreflang', code);
        if (code === 'ar') a.setAttribute('dir', 'rtl');
        a.textContent = LANG_NAMES[code] || code;
        li.appendChild(a);
        drawerUl.appendChild(li);
      });
    }
  }

  // Toggle dropdown
  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    var open = wrapper.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // Close on outside click
  document.addEventListener('click', function () {
    wrapper.classList.remove('open');
    btn.setAttribute('aria-expanded', 'false');
  });

  // Close on Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      wrapper.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    }
  });
}());
