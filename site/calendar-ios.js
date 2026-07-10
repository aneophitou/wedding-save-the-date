var ICS_HTTPS_URL = 'https://wedding.neophitou.com/AndreasAndNikoletaWedding.ics';
var ICS_WEBCAL_URL = 'webcal://wedding.neophitou.com/AndreasAndNikoletaWedding.ics';

function isSafariIos() {
  return /^((?!chrome|android|crios|fxios|edgios|brave).)*safari/i.test(navigator.userAgent);
}

function removeWebComponent() {
  var webComponent = document.querySelector('add-to-calendar-button');
  if (webComponent) {
    webComponent.remove();
  }
}

function openIosCalendar(event) {
  event.preventDefault();

  var targetUrl = isSafariIos() ? ICS_HTTPS_URL : ICS_WEBCAL_URL;
  window.location.assign(targetUrl);
}

function initIosCalendarLink() {
  if (!document.documentElement.classList.contains('ios')) {
    return;
  }

  removeWebComponent();

  var iosLink = document.getElementById('calendar-ios-link');
  if (!iosLink) {
    return;
  }

  iosLink.addEventListener('click', openIosCalendar);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initIosCalendarLink);
} else {
  initIosCalendarLink();
}
