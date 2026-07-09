(function () {
  "use strict";

  var app = window.UmarPortfolio || {};
  var ready = app.whenReady || function (callback) { callback(); };
  var observedElements = new WeakSet();
  var observer = null;

  function collectRevealTargets(root) {
    var context = root || document;
    var targets = Array.from(context.querySelectorAll ? context.querySelectorAll("[data-reveal]") : []);

    if (context.matches && context.matches("[data-reveal]")) {
      targets.unshift(context);
    }

    return targets;
  }

  function revealElement(element) {
    element.classList.add("is-visible");
  }

  function observeReveals(root) {
    var targets = collectRevealTargets(root);

    if (!targets.length) {
      return;
    }

    if (!observer) {
      targets.forEach(revealElement);
      return;
    }

    targets.forEach(function (element) {
      if (observedElements.has(element) || element.classList.contains("is-visible")) {
        return;
      }

      observedElements.add(element);
      observer.observe(element);
    });
  }

  app.observeReveals = observeReveals;
  window.UmarPortfolio = app;

  ready(function () {
    if (!("IntersectionObserver" in window)) {
      observeReveals(document);
      return;
    }

    observer = new IntersectionObserver(
      function (entries, instance) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            revealElement(entry.target);
            instance.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.15,
        rootMargin: "0px 0px -8% 0px",
      }
    );

    observeReveals(document);

    window.addEventListener("portfolio:contentchange", function () {
      observeReveals(document);
    });
  });
})();
