(function () {
  var overlay = document.createElement('div');
  overlay.id = 'lb-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-label', 'Image viewer');
  overlay.innerHTML = '<button id="lb-close" aria-label="Close image viewer">&times;</button><img id="lb-img" alt="">';
  document.body.appendChild(overlay);

  var lbImg = document.getElementById('lb-img');
  var lbClose = document.getElementById('lb-close');

  function open(src, alt) {
    lbImg.src = src;
    lbImg.alt = alt || '';
    overlay.classList.add('lb-active');
    document.body.style.overflow = 'hidden';
    lbClose.focus();
  }

  function close() {
    overlay.classList.remove('lb-active');
    document.body.style.overflow = '';
    setTimeout(function () { lbImg.src = ''; }, 200);
  }

  lbClose.addEventListener('click', close);

  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) close();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') close();
  });

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.article-content img').forEach(function (img) {
      img.classList.add('lb-trigger');
      img.setAttribute('title', 'Click to enlarge');
      img.addEventListener('click', function () {
        open(img.src, img.alt);
      });
    });
  });
}());
