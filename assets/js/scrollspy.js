(function () {
  "use strict";

  var app = window.UmarPortfolio || {};
  var ready = app.whenReady || function (callback) { callback(); };
  var throttle = app.throttle || function (callback) { return callback; };

  ready(function () {
    var links = Array.from(document.querySelectorAll('.navbar .nav-link[href^="#"]'));

    if (!links.length) {
      return;
    }

    var sections = links
      .map(function (link) {
        return document.querySelector(link.getAttribute("href"));
      })
      .filter(Boolean);

    function setActive(sectionId) {
      links.forEach(function (link) {
        var isActive = link.getAttribute("href") === "#" + sectionId;
        link.classList.toggle("active", isActive);

        if (isActive) {
          link.setAttribute("aria-current", "page");
        } else {
          link.removeAttribute("aria-current");
        }
      });
    }

    function getNavbarOffset() {
      var navbar = document.getElementById("navbar");
      var height = navbar ? navbar.getBoundingClientRect().height : 84;

      return height + 56;
    }

    function getCurrentSectionId() {
      var offset = getNavbarOffset();
      var scrollPosition = window.scrollY + offset;
      var current = sections[0];

      sections.forEach(function (section) {
        if (section.offsetTop <= scrollPosition) {
          current = section;
        }
      });

      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) {
        current = sections[sections.length - 1];
      }

      return current.id;
    }

    function updateActiveSection() {
      setActive(getCurrentSectionId());
    }

    if (!sections.length) {
      return;
    }

    updateActiveSection();

    window.addEventListener("scroll", throttle(updateActiveSection, 80), { passive: true });
    window.addEventListener("resize", throttle(updateActiveSection, 150), { passive: true });
    window.addEventListener("hashchange", updateActiveSection);
    window.addEventListener("portfolio:contentchange", updateActiveSection);

    links.forEach(function (link) {
      link.addEventListener("click", function () {
        var id = link.getAttribute("href").replace("#", "");
        setActive(id);
        window.setTimeout(updateActiveSection, 220);
      });
    });
  });
})();
