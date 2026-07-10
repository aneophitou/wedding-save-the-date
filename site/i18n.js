(function () {
  var DICT = {
    en: {
      lang: 'en',
      title: 'Andreas & Nikoleta \u2014 Save the Date',
      description:
        "Save the date for Andreas and Nikoleta's wedding on 11 July 2027.",
      titleAria:
        'Save the date: Andreas and Nikoleta, 11 July 2027, Nicosia, Cyprus',
      date: '11.07.27',
      std: 'Save The Date',
      names: 'Andreas + Nikoleta',
      location: 'NICOSIA, CYPRUS',
      followup: 'FORMAL INVITATION TO FOLLOW',
      calendar: 'Add to Calendar',
    },
    el: {
      lang: 'el',
      title: '\u0391\u03bd\u03c4\u03c1\u03ad\u03b1\u03c2 & \u039d\u03b9\u03ba\u03bf\u03bb\u03ad\u03c4\u03b1 \u2014 \u039a\u03c1\u03b1\u03c4\u03ae\u03c3\u03c4\u03b5 \u03c4\u03b7\u03bd \u0397\u03bc\u03b5\u03c1\u03bf\u03bc\u03b7\u03bd\u03af\u03b1',
      description:
        '\u039a\u03c1\u03b1\u03c4\u03ae\u03c3\u03c4\u03b5 \u03c4\u03b7\u03bd \u03b7\u03bc\u03b5\u03c1\u03bf\u03bc\u03b7\u03bd\u03af\u03b1 \u03b3\u03b9\u03b1 \u03c4\u03bf\u03bd \u03b3\u03ac\u03bc\u03bf \u03c4\u03bf\u03c5 \u0391\u03bd\u03c4\u03c1\u03ad\u03b1 \u03ba\u03b1\u03b9 \u03c4\u03b7\u03c2 \u039d\u03b9\u03ba\u03bf\u03bb\u03ad\u03c4\u03b1\u03c2 \u2014 11 \u0399\u03bf\u03c5\u03bb\u03af\u03bf\u03c5 2027.',
      titleAria:
        '\u039a\u03c1\u03b1\u03c4\u03ae\u03c3\u03c4\u03b5 \u03c4\u03b7\u03bd \u03b7\u03bc\u03b5\u03c1\u03bf\u03bc\u03b7\u03bd\u03af\u03b1: \u0391\u03bd\u03c4\u03c1\u03ad\u03b1\u03c2 \u03ba\u03b1\u03b9 \u039d\u03b9\u03ba\u03bf\u03bb\u03ad\u03c4\u03b1, 11 \u0399\u03bf\u03c5\u03bb\u03af\u03bf\u03c5 2027, \u039b\u03b5\u03c5\u03ba\u03c9\u03c3\u03af\u03b1, \u039a\u03cd\u03c0\u03c1\u03bf\u03c2',
      date: '11.07.27',
      std: '\u039a\u03c1\u03b1\u03c4\u03ae\u03c3\u03c4\u03b5 \u03c4\u03b7\u03bd \u0397\u03bc\u03b5\u03c1\u03bf\u03bc\u03b7\u03bd\u03af\u03b1',
      names: '\u0391\u03bd\u03c4\u03c1\u03ad\u03b1\u03c2 + \u039d\u03b9\u03ba\u03bf\u03bb\u03ad\u03c4\u03b1',
      location: '\u039b\u0395\u03a5\u039a\u03a9\u03a3\u0399\u0391, \u039a\u03a5\u03a0\u03a1\u039f\u03a3',
      followup:
        '\u0395\u03a0\u0399\u03a3\u0397\u039c\u0397 \u03a0\u03a1\u039f\u03a3\u039a\u039b\u0397\u03a3\u0397 \u0398\u0391 \u0391\u039a\u039f\u039b\u039f\u03a5\u0398\u0397\u03a3\u0395\u0399',
      calendar:
        '\u03a0\u03c1\u03bf\u03c3\u03b8\u03ae\u03ba\u03b7 \u03c3\u03c4\u03bf \u0397\u03bc\u03b5\u03c1\u03bf\u03bb\u03cc\u03b3\u03b9\u03bf',
    },
  };

  function detectLang() {
    try {
      var override = new URLSearchParams(window.location.search)
        .get('lang');
      if (override) {
        override = override.toLowerCase();
        if (override.indexOf('el') === 0) return 'el';
        if (override.indexOf('en') === 0) return 'en';
      }
    } catch (e) {
      /* URLSearchParams unavailable */
    }

    var langs =
      navigator.languages && navigator.languages.length
        ? navigator.languages
        : [navigator.language || 'en'];
    for (var i = 0; i < langs.length; i++) {
      if (langs[i] && langs[i].toLowerCase().indexOf('el') === 0) {
        return 'el';
      }
    }
    return 'en';
  }

  var lang = detectLang();
  var strings = DICT[lang];
  window.__weddingLang = lang;
  window.__weddingStrings = strings;

  // Applied synchronously (script runs before the stylesheet) so the correct
  // language class is set without a flash.
  var root = document.documentElement;
  root.lang = strings.lang;
  root.classList.add('lang-' + lang);
  document.title = strings.title;

  var metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.setAttribute('content', strings.description);
  }

  function localizeBody() {
    var t = window.__weddingStrings || DICT.en;

    var nodes = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < nodes.length; i++) {
      var key = nodes[i].getAttribute('data-i18n');
      if (t[key] != null) {
        nodes[i].textContent = t[key];
      }
    }

    var titleBlock = document.querySelector('.title-block');
    if (titleBlock && t.titleAria) {
      titleBlock.setAttribute('aria-label', t.titleAria);
    }

    var atc = document.querySelector('add-to-calendar-button');
    if (atc) {
      atc.setAttribute('label', t.calendar);
      if (atc.shadowRoot) {
        // Force the web component to re-render with the new label.
        var instance = parseInt(atc.getAttribute('instance') || '1', 10);
        atc.setAttribute('instance', String(instance + 1));
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', localizeBody);
  } else {
    localizeBody();
  }
})();
