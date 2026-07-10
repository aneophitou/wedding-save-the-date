function isIosDevice() {
  return (
    /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  );
}

function enableIosCalendarLink() {
  if (!isIosDevice()) {
    return;
  }

  const webComponent = document.querySelector('add-to-calendar-button');
  const iosLink = document.getElementById('calendar-ios-link');

  if (!webComponent || !iosLink) {
    return;
  }

  webComponent.hidden = true;
  iosLink.hidden = false;
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', enableIosCalendarLink);
} else {
  enableIosCalendarLink();
}
