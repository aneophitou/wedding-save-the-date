var ICS_HTTPS_URL = 'https://wedding.neophitou.com/AndreasAndNikoletaWedding.ics';
var ICS_FILENAME = 'AndreasAndNikoletaWedding.ics';

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

  iosLink.setAttribute('href', ICS_HTTPS_URL);

  if (isSafariIos()) {
    // Safari opens the .ics directly with a one-time Apple Calendar add
    // prompt, so it navigates to the file (no download attribute).
    return;
  }

  // Chrome, Brave, and other iOS browsers blank the page when navigating
  // to an .ics. Downloading the file instead keeps the page intact: the
  // browser saves the file and the guest opens it into Apple Calendar from
  // the download banner.
  iosLink.setAttribute('download', ICS_FILENAME);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initIosCalendarLink);
} else {
  initIosCalendarLink();
}
