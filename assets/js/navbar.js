(function () {
  "use strict";

  var app = window.UmarPortfolio || {};
  var ready = app.whenReady || function (callback) { callback(); };

  ready(function () {
    var navbar = document.getElementById("navbar");
    var navCollapse = document.getElementById("primaryNav");
    var toggler = document.querySelector(".navbar-toggler");
    var navLinks = Array.from(document.querySelectorAll('.navbar .nav-link[href^="#"]'));

    if (!navbar) {
      return;
    }

    function updateScrolledState() {
      navbar.classList.toggle("is-scrolled", window.scrollY > 10);
    }

    function setTogglerIcon(isOpen) {
      if (!toggler) {
        return;
      }

      var icon = toggler.querySelector("i");
      toggler.setAttribute("aria-expanded", isOpen ? "true" : "false");

      if (icon) {
        icon.className = isOpen ? "bi bi-x-lg fs-4" : "bi bi-list fs-4";
      }
    }

    updateScrolledState();
    window.addEventListener("scroll", updateScrolledState, { passive: true });

    navLinks.forEach(function (link) {
      link.addEventListener("click", function () {
        if (!navCollapse || !window.bootstrap || window.innerWidth >= 992) {
          return;
        }

        var collapse = bootstrap.Collapse.getOrCreateInstance(navCollapse, {
          toggle: false,
        });

        collapse.hide();
      });
    });

    if (navCollapse) {
      navCollapse.addEventListener("shown.bs.collapse", function () {
        setTogglerIcon(true);
      });

      navCollapse.addEventListener("hidden.bs.collapse", function () {
        setTogglerIcon(false);
      });
    }

    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape" || !navCollapse || !window.bootstrap) {
        return;
      }

      bootstrap.Collapse.getOrCreateInstance(navCollapse, {
        toggle: false,
      }).hide();
    });
  });
})();
