var ICS_HTTPS_URL = 'https://wedding.neophitou.com/AndreasAndNikoletaWedding.ics';
var ICS_WEBCAL_URL = 'webcal://wedding.neophitou.com/AndreasAndNikoletaWedding.ics';

function isSafariIos() {
  var ua = navigator.userAgent;
  return /safari/i.test(ua) && !/crios|fxios|edgios|android/i.test(ua);
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

  // Safari opens an https .ics with a one-time "add event" prompt.
  // Chrome, Brave, and other iOS browsers cannot hand off a downloaded
  // .ics, so they use the webcal:// scheme, which iOS intercepts and
  // opens in Calendar without navigating (and blanking) the page.
  iosLink.setAttribute('href', isSafariIos() ? ICS_HTTPS_URL : ICS_WEBCAL_URL);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initIosCalendarLink);
} else {
  initIosCalendarLink();
}
