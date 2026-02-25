/*  Theme toggle — injects sun/moon button into nav, handles clicks.
    Anti-flash detection runs inline in <head> (see theme-init snippet).
    This file handles the interactive toggle only.                       */
(function () {
  var MOON = '<svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  var SUN  = '<svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';

  function toggle() {
    var html = document.documentElement;
    var current = html.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    try { localStorage.setItem('stv-theme', next); } catch (e) {}
  }

  // Inject toggle button into desktop nav (after nav-links)
  var navInner = document.querySelector('.nav-inner');
  if (navInner) {
    var btn = document.createElement('button');
    btn.className = 'theme-toggle';
    btn.setAttribute('aria-label', 'Toggle dark mode');
    btn.innerHTML = MOON + SUN;
    // Insert before hamburger (or at end)
    var hamburger = navInner.querySelector('.nav-hamburger');
    if (hamburger) {
      navInner.insertBefore(btn, hamburger);
    } else {
      navInner.appendChild(btn);
    }
    btn.addEventListener('click', toggle);
  }

  // Inject toggle into mobile drawer too
  var drawer = document.getElementById('nav-drawer');
  if (drawer) {
    var li = document.createElement('li');
    li.style.borderBottom = 'none';
    li.style.padding = '12px 0';
    var mBtn = document.createElement('button');
    mBtn.className = 'theme-toggle';
    mBtn.setAttribute('aria-label', 'Toggle dark mode');
    mBtn.innerHTML = MOON + SUN;
    mBtn.style.margin = '0';
    li.appendChild(mBtn);
    var ul = drawer.querySelector('ul');
    if (ul) ul.appendChild(li);
    mBtn.addEventListener('click', toggle);
  }
}());
