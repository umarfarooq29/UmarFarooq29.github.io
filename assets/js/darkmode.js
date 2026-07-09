(function () {
  "use strict";

  var app = window.UmarPortfolio || {};
  var ready = app.whenReady || function (callback) { callback(); };
  var storageKey = "umar-portfolio-theme";
  var root = document.documentElement;
  var systemQuery = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function getStoredTheme() {
    try {
      return localStorage.getItem(storageKey);
    } catch (error) {
      return null;
    }
  }

  function storeTheme(theme) {
    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {
      return;
    }
  }

  function getPreferredTheme() {
    return getStoredTheme() || root.getAttribute("data-theme") || (systemQuery && systemQuery.matches ? "dark" : "light");
  }

  function updateToggle(toggle, theme) {
    if (!toggle) {
      return;
    }

    var label = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
    var icon = toggle.querySelector("i");

    toggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    toggle.setAttribute("aria-label", label);
    toggle.setAttribute("title", label);

    if (icon) {
      icon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars";
    }
  }

  function applyTheme(theme, options) {
    var nextTheme = theme === "dark" ? "dark" : "light";
    var shouldStore = !options || options.store !== false;

    root.setAttribute("data-theme", nextTheme);

    if (shouldStore) {
      storeTheme(nextTheme);
    }

    window.dispatchEvent(new CustomEvent("portfolio:themechange", {
      detail: {
        theme: nextTheme,
      },
    }));
  }

  app.setTheme = applyTheme;
  app.getTheme = function () {
    return root.getAttribute("data-theme") === "dark" ? "dark" : "light";
  };
  window.UmarPortfolio = app;

  ready(function () {
    var toggle = document.querySelector("[data-theme-toggle]");
    var initialTheme = getPreferredTheme();

    applyTheme(initialTheme, {
      store: Boolean(getStoredTheme()),
    });
    updateToggle(toggle, initialTheme);

    if (toggle) {
      toggle.addEventListener("click", function () {
        var currentTheme = app.getTheme();
        var nextTheme = currentTheme === "dark" ? "light" : "dark";
        applyTheme(nextTheme);
        updateToggle(toggle, nextTheme);
      });
    }

    if (systemQuery && !getStoredTheme()) {
      systemQuery.addEventListener("change", function (event) {
        var systemTheme = event.matches ? "dark" : "light";
        applyTheme(systemTheme, {
          store: false,
        });
        updateToggle(toggle, systemTheme);
      });
    }
  });
})();
