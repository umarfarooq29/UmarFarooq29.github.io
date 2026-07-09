(function () {
  "use strict";

  var app = window.UmarPortfolio || {};

  function whenReady(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
      return;
    }

    callback();
  }

  function qs(selector, context) {
    return (context || document).querySelector(selector);
  }

  function qsa(selector, context) {
    return Array.from((context || document).querySelectorAll(selector));
  }

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function throttle(callback, wait) {
    var timeoutId = null;
    var lastArgs = null;

    return function throttled() {
      lastArgs = arguments;

      if (timeoutId) {
        return;
      }

      timeoutId = window.setTimeout(function () {
        timeoutId = null;
        callback.apply(null, lastArgs);
      }, wait);
    };
  }

  function setScrollTopButton() {
    var scrollTopButton = qs("#scrollTop");

    if (!scrollTopButton) {
      return;
    }

    function toggleScrollTop() {
      scrollTopButton.classList.toggle("is-visible", window.scrollY > 500);
    }

    toggleScrollTop();
    window.addEventListener("scroll", throttle(toggleScrollTop, 80), { passive: true });

    scrollTopButton.addEventListener("click", function () {
      window.scrollTo({
        top: 0,
        behavior: prefersReducedMotion() ? "auto" : "smooth",
      });
    });
  }

  function setCurrentYear() {
    var currentYear = qs("#currentYear");

    if (currentYear) {
      currentYear.textContent = new Date().getFullYear();
    }
  }

  function markPageReady() {
    document.body.classList.add("is-loaded");
  }

  app.whenReady = app.whenReady || whenReady;
  app.qs = app.qs || qs;
  app.qsa = app.qsa || qsa;
  app.prefersReducedMotion = app.prefersReducedMotion || prefersReducedMotion;
  app.throttle = app.throttle || throttle;
  window.UmarPortfolio = app;

  whenReady(function () {
    setCurrentYear();
    setScrollTopButton();
    markPageReady();
  });
})();
