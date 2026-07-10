var ICS_HTTPS_URL = 'https://wedding.neophitou.com/AndreasAndNikoletaWedding.ics';
var ICS_SAFARI_URL =
  'x-safari-https://wedding.neophitou.com/AndreasAndNikoletaWedding.ics';

function isSafariIos() {
  var ua = navigator.userAgent;
  return /safari/i.test(ua) && !/crios|fxios|edgios|android/i.test(ua);
}

function openViaSafari(event) {
  event.preventDefault();

  // If handing off to Safari succeeds, this page is backgrounded, so the
  // fallback is cancelled. On iOS versions where x-safari-https is not
  // supported (e.g. iOS 16) the page stays visible and we fall back to
  // opening the .ics directly.
  var fallback = window.setTimeout(function () {
    window.location.href = ICS_HTTPS_URL;
  }, 1200);

  function onVisibilityChange() {
    if (document.hidden) {
      window.clearTimeout(fallback);
      document.removeEventListener('visibilitychange', onVisibilityChange);
    }
  }

  document.addEventListener('visibilitychange', onVisibilityChange);
  window.location.href = ICS_SAFARI_URL;
}

function initIosCalendarLink() {
  if (!document.documentElement.classList.contains('ios')) {
    return;
  }

  var webComponent = document.querySelector('add-to-calendar-button');
  if (webComponent) {
    webComponent.remove();
  }

  var iosLink = document.getElementById('calendar-ios-link');
  if (!iosLink) {
    return;
  }

  if (isSafariIos()) {
    // Safari opens the .ics directly with a one-time Apple Calendar add.
    iosLink.setAttribute('href', ICS_HTTPS_URL);
    return;
  }

  // Chrome, Brave, and other iOS browsers cannot open an .ics themselves,
  // so hand the link off to Safari via the x-safari-https scheme. Safari
  // then adds the one-time event to Apple Calendar. The href works even
  // without JS; the click handler adds a fallback for unsupported iOS.
  iosLink.setAttribute('href', ICS_SAFARI_URL);
  iosLink.addEventListener('click', openViaSafari);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initIosCalendarLink);
} else {
  initIosCalendarLink();
}
