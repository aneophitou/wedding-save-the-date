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

  // Safari is the only iOS browser that can open a single-event .ics file
  // directly, opening Apple Calendar with a one-time add prompt.
  //
  // Chrome, Brave, and other iOS browsers are chromeless WebViews that
  // Apple blocks from opening .ics files, and there is no Apple Calendar
  // "add event" URL scheme. The only way to reach Apple Calendar in those
  // browsers is the webcal:// scheme, which iOS intercepts natively (no
  // white screen). It adds the event on the correct date via a subscribed
  // calendar, which is an unavoidable Apple platform limitation.
  iosLink.setAttribute('href', isSafariIos() ? ICS_HTTPS_URL : ICS_WEBCAL_URL);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initIosCalendarLink);
} else {
  initIosCalendarLink();
}
