/* Newsletter signup handler — posts to VPS API */
(function() {
  var API = 'https://app.socialtradingvlog.com/api/subscribe';

  document.addEventListener('submit', function(e) {
    var form = e.target;
    if (!form.classList.contains('newsletter-form')) return;
    e.preventDefault();

    var email = form.querySelector('input[type="email"]').value.trim();
    if (!email) return;

    var btn = form.querySelector('button');
    var msg = form.querySelector('.newsletter-msg');
    var origText = btn.textContent;
    btn.textContent = 'Subscribing...';
    btn.disabled = true;

    fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, source: location.pathname })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data.success) {
        msg.textContent = 'You\u2019re in! Check your inbox.';
        msg.className = 'newsletter-msg newsletter-success';
        form.querySelector('input[type="email"]').value = '';
        if (typeof gtag === 'function') {
          gtag('event', 'newsletter_signup', {
            event_category: 'engagement',
            event_label: location.pathname
          });
        }
      } else {
        msg.textContent = data.error || 'Something went wrong.';
        msg.className = 'newsletter-msg newsletter-error';
      }
    })
    .catch(function() {
      msg.textContent = 'Connection error. Try again.';
      msg.className = 'newsletter-msg newsletter-error';
    })
    .finally(function() {
      btn.textContent = origText;
      btn.disabled = false;
    });
  });
})();
