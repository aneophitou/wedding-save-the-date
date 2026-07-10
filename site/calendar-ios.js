var ICS_HTTPS_URL = 'https://wedding.neophitou.com/AndreasAndNikoletaWedding.ics';

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

  // Every iOS browser links directly to the single-event .ics file. Safari
  // opens Apple Calendar with a one-time add prompt. Chrome, Brave, and
  // other iOS browsers also add the one-time event, then land on a blank
  // page afterwards -- an accepted trade-off to avoid a calendar
  // subscription, since the event is already added at that point.
  iosLink.setAttribute('href', ICS_HTTPS_URL);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initIosCalendarLink);
} else {
  initIosCalendarLink();
}
