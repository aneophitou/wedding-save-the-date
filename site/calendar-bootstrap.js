(function () {
  var isIos =
    /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

  if (isIos) {
    document.documentElement.classList.add('ios');
    return;
  }

  var script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/add-to-calendar-button@2';
  script.async = true;
  script.defer = true;
  document.head.appendChild(script);
})();
