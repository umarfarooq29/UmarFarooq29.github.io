(function () {
  "use strict";

  var app = window.UmarPortfolio || {};
  var ready = app.whenReady || function (callback) { callback(); };
  var prefersReducedMotion = app.prefersReducedMotion || function () { return false; };

  ready(function () {
    var targets = Array.from(document.querySelectorAll("[data-typewriter]"));

    if (!targets.length) {
      return;
    }

    targets.forEach(function (target) {
      var words = (target.getAttribute("data-roles") || target.textContent || "")
        .split("|")
        .map(function (word) {
          return word.trim();
        })
        .filter(Boolean);

      if (!words.length) {
        return;
      }

      target.setAttribute("aria-label", words.join(", "));

      if (prefersReducedMotion()) {
        target.textContent = words[0];
        return;
      }

      var wordIndex = 0;
      var letterIndex = 0;
      var isDeleting = false;
      var typingDelay = 76;
      var deletingDelay = 38;
      var holdDelay = 1350;

      target.classList.add("typewriter-text");

      function tick() {
        var currentWord = words[wordIndex];

        if (isDeleting) {
          letterIndex -= 1;
        } else {
          letterIndex += 1;
        }

        target.textContent = currentWord.slice(0, letterIndex);

        if (!isDeleting && letterIndex === currentWord.length) {
          window.setTimeout(function () {
            isDeleting = true;
            tick();
          }, holdDelay);
          return;
        }

        if (isDeleting && letterIndex === 0) {
          isDeleting = false;
          wordIndex = (wordIndex + 1) % words.length;
        }

        window.setTimeout(tick, isDeleting ? deletingDelay : typingDelay);
      }

      target.textContent = "";
      tick();
    });
  });
})();
