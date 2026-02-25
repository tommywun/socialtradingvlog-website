(function () {
  var btn = document.getElementById('nav-hamburger');
  var drawer = document.getElementById('nav-drawer');
  if (!btn || !drawer) return;

  btn.addEventListener('click', function () {
    var open = drawer.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.body.style.overflow = open ? 'hidden' : '';
  });

  // Close on link click
  drawer.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      drawer.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  // Close on Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && drawer.classList.contains('open')) {
      drawer.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      btn.focus();
    }
  });
}());

/* TOC collapse/expand in sidebar */
(function () {
  document.querySelectorAll('.toc h4').forEach(function (h4) {
    var toc = h4.closest('.toc');
    if (!toc) return;
    // Start collapsed in sidebar (sticky context) to save space
    if (toc.closest('.article-sidebar')) {
      toc.classList.add('collapsed');
    }
    h4.addEventListener('click', function () {
      toc.classList.toggle('collapsed');
    });
  });
}());
