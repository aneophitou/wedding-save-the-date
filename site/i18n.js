(function () {
  var STORAGE_KEY = 'wedding-lang';

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
      switchEn: 'English',
      switchEl: 'Greek',
    },
    el: {
      lang: 'el',
      title:
        '\u0391\u03bd\u03b4\u03c1\u03ad\u03b1\u03c2 & \u039d\u03b9\u03ba\u03bf\u03bb\u03ad\u03c4\u03b1 \u2014 Save the Date',
      description:
        '\u0391\u03c0\u03bf\u03b8\u03b7\u03ba\u03b5\u03cd\u03c3\u03c4\u03b5 \u03c4\u03b7\u03bd \u03b7\u03bc\u03b5\u03c1\u03bf\u03bc\u03b7\u03bd\u03af\u03b1 \u03b3\u03b9\u03b1 \u03c4\u03bf\u03bd \u03b3\u03ac\u03bc\u03bf \u03c4\u03bf\u03c5 \u0391\u03bd\u03b4\u03c1\u03ad\u03b1 \u03ba\u03b1\u03b9 \u03c4\u03b7\u03c2 \u039d\u03b9\u03ba\u03bf\u03bb\u03ad\u03c4\u03b1\u03c2 \u2014 11 \u0399\u03bf\u03c5\u03bb\u03af\u03bf\u03c5 2027.',
      titleAria:
        '\u0391\u03c0\u03bf\u03b8\u03b7\u03ba\u03b5\u03cd\u03c3\u03c4\u03b5 \u03c4\u03b7\u03bd \u03b7\u03bc\u03b5\u03c1\u03bf\u03bc\u03b7\u03bd\u03af\u03b1: \u0391\u03bd\u03b4\u03c1\u03ad\u03b1\u03c2 \u03ba\u03b1\u03b9 \u039d\u03b9\u03ba\u03bf\u03bb\u03ad\u03c4\u03b1, 11 \u0399\u03bf\u03c5\u03bb\u03af\u03bf\u03c5 2027, \u039b\u03b5\u03c5\u03ba\u03c9\u03c3\u03af\u03b1, \u039a\u03cd\u03c0\u03c1\u03bf\u03c2',
      date: '11.07.27',
      names: '\u0391\u03bd\u03b4\u03c1\u03ad\u03b1\u03c2 + \u039d\u03b9\u03ba\u03bf\u03bb\u03ad\u03c4\u03b1',
      location: '\u039b\u0395\u03a5\u039a\u03a9\u03a3\u0399\u0391, \u039a\u03a5\u03a0\u03a1\u039f\u03a3',
      followup:
        '\u0398\u0391 \u0391\u039a\u039f\u039b\u039f\u03a5\u0398\u0397\u03a3\u0395\u0399 \u0395\u03a0\u0399\u03a3\u0397\u039c\u0397 \u03a0\u03a1\u039f\u03a3\u039a\u039b\u0397\u03a3\u0397',
      calendar:
        '\u03a0\u03c1\u03bf\u03c3\u03b8\u03ae\u03ba\u03b7 \u03c3\u03c4\u03bf \u0397\u03bc\u03b5\u03c1\u03bf\u03bb\u03cc\u03b3\u03b9\u03bf',
      switchEn: 'English',
      switchEl: '\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac',
    },
  };

  function readStoredLang() {
    try {
      var stored = localStorage.getItem(STORAGE_KEY);
      if (stored === 'en' || stored === 'el') {
        return stored;
      }
    } catch (e) {
      /* localStorage unavailable */
    }
    return null;
  }

  function storeLang(lang) {
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      /* localStorage unavailable */
    }
  }

  function detectLang() {
    var stored = readStoredLang();
    if (stored) {
      return stored;
    }

    try {
      var override = new URLSearchParams(window.location.search).get('lang');
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

  function applyLang(lang) {
    var strings = DICT[lang];
    window.__weddingLang = lang;
    window.__weddingStrings = strings;

    var root = document.documentElement;
    root.lang = strings.lang;
    root.classList.remove('lang-en', 'lang-el');
    root.classList.add('lang-' + lang);
    document.title = strings.title;

    var metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute('content', strings.description);
    }

    var nodes = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < nodes.length; i++) {
      var key = nodes[i].getAttribute('data-i18n');
      if (strings[key] != null) {
        nodes[i].textContent = strings[key];
      }
    }

    var titleBlock = document.querySelector('.title-block');
    if (titleBlock && strings.titleAria) {
      titleBlock.setAttribute('aria-label', strings.titleAria);
    }

    var switchEn = document.querySelector('[data-lang-switch="en"]');
    var switchEl = document.querySelector('[data-lang-switch="el"]');
    if (switchEn) {
      switchEn.setAttribute('aria-pressed', lang === 'en' ? 'true' : 'false');
      switchEn.setAttribute('aria-label', strings.switchEn);
    }
    if (switchEl) {
      switchEl.setAttribute('aria-pressed', lang === 'el' ? 'true' : 'false');
      switchEl.setAttribute('aria-label', strings.switchEl);
    }

    var atc = document.querySelector('add-to-calendar-button');
    if (atc) {
      atc.setAttribute('label', strings.calendar);
      if (atc.shadowRoot) {
        var instance = parseInt(atc.getAttribute('instance') || '1', 10);
        atc.setAttribute('instance', String(instance + 1));
      }
    }
  }

  function setLang(lang) {
    if (lang !== 'en' && lang !== 'el') {
      return;
    }
    storeLang(lang);
    applyLang(lang);
  }

  window.__weddingSetLang = setLang;

  var initialLang = detectLang();
  applyLang(initialLang);

  function bindLanguageSwitcher() {
    var buttons = document.querySelectorAll('[data-lang-switch]');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener('click', function (event) {
        var nextLang = event.currentTarget.getAttribute('data-lang-switch');
        setLang(nextLang);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindLanguageSwitcher);
  } else {
    bindLanguageSwitcher();
  }
})();
