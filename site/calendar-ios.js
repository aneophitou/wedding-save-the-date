var ICS_HTTPS_URL = 'https://wedding.neophitou.com/AndreasAndNikoletaWedding.ics';

function isSafariIos() {
  var ua = navigator.userAgent;
  return /safari/i.test(ua) && !/crios|fxios|edgios|android/i.test(ua);
}

function googleCalendarUrl() {
  var params = [
    'action=TEMPLATE',
    'text=' + encodeURIComponent("Andreas and Nikoleta's Wedding"),
    'dates=20270711T180000/20270712T020000',
    'ctz=Europe/Nicosia',
    'location=' + encodeURIComponent('Archangelou Michael'),
    'details=' +
      encodeURIComponent(
        'Ceremony at the Church of Archangelos Michael in Archangelos.\n' +
          'Reception at Ktima Koushioumis.'
      ),
  ];
  return 'https://calendar.google.com/calendar/render?' + params.join('&');
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
    // Safari is the only iOS browser that can open a single-event .ics
    // file directly, opening Apple Calendar with an add prompt.
    iosLink.setAttribute('href', ICS_HTTPS_URL);
    return;
  }

  // Chrome, Brave, and other iOS browsers are chromeless WebViews that
  // Apple blocks from opening .ics files. Rather than forcing a calendar
  // *subscription* via webcal://, add the single event through Google
  // Calendar, which works in every browser and adds the real date.
  iosLink.setAttribute('href', googleCalendarUrl());
  iosLink.setAttribute('target', '_blank');
  iosLink.setAttribute('rel', 'noopener');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initIosCalendarLink);
} else {
  initIosCalendarLink();
}
