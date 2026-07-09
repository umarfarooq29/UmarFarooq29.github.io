(function () {
  "use strict";

  var app = window.UmarPortfolio || {};
  var ready = app.whenReady || function (callback) { callback(); };
  var prefersReducedMotion = app.prefersReducedMotion || function () { return false; };

  function formatNumber(value, suffix) {
    return Math.round(value).toLocaleString() + (suffix || "");
  }

  function fetchJson(path) {
    if (!window.fetch) {
      return Promise.resolve(null);
    }

    return fetch(path, {
      cache: "no-store",
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Unable to load " + path);
        }

        return response.json();
      })
      .catch(function () {
        return null;
      });
  }

  function countSkillItems(data) {
    if (!Array.isArray(data)) {
      return null;
    }

    return data.reduce(function (total, group) {
      var items = Array.isArray(group.items) ? group.items : Array.isArray(group.skills) ? group.skills : [];
      return total + items.length;
    }, 0);
  }

  function countProjectTracks(data) {
    if (!Array.isArray(data)) {
      return null;
    }

    var tracks = new Set();

    data.forEach(function (project) {
      if (project.category) {
        tracks.add(project.category);
      }
    });

    return tracks.size || data.length;
  }

  function countRoles() {
    var typewriter = document.querySelector("[data-typewriter]");
    var roles = typewriter ? (typewriter.getAttribute("data-roles") || "").split("|").filter(Boolean) : [];

    return roles.length || null;
  }

  function setCounterTarget(counter, value) {
    if (Number.isFinite(value) && value > 0) {
      counter.setAttribute("data-target", String(value));
      counter.textContent = "0";
      delete counter.dataset.counted;
    }
  }

  function hydrateLiveStats(counters) {
    var stats = counters.filter(function (counter) {
      return counter.hasAttribute("data-live-stat");
    });

    if (!stats.length) {
      return Promise.resolve();
    }

    return Promise.all([
      fetchJson("data/skills.json"),
      fetchJson("data/projects.json"),
    ]).then(function (results) {
      var skills = results[0];
      var projects = results[1];

      stats.forEach(function (counter) {
        var type = counter.getAttribute("data-live-stat");

        if (type === "roles") {
          setCounterTarget(counter, countRoles());
        }

        if (type === "skills") {
          setCounterTarget(counter, countSkillItems(skills));
        }

        if (type === "projects") {
          setCounterTarget(counter, countProjectTracks(projects));
        }
      });
    });
  }

  ready(function () {
    var counters = Array.from(document.querySelectorAll("[data-counter]"));

    if (!counters.length) {
      return;
    }

    function animateCounter(counter) {
      if (counter.dataset.counted === "true") {
        return;
      }

      var target = Number(counter.getAttribute("data-target") || counter.textContent || 0);
      var suffix = counter.getAttribute("data-suffix") || "";
      var duration = Number(counter.getAttribute("data-duration") || 1200);
      var startTime = null;

      counter.dataset.counted = "true";

      if (prefersReducedMotion() || !Number.isFinite(target)) {
        counter.textContent = formatNumber(target || 0, suffix);
        return;
      }

      function step(timestamp) {
        if (!startTime) {
          startTime = timestamp;
        }

        var progress = Math.min((timestamp - startTime) / duration, 1);
        var easedProgress = 1 - Math.pow(1 - progress, 3);
        counter.textContent = formatNumber(target * easedProgress, suffix);

        if (progress < 1) {
          window.requestAnimationFrame(step);
        }
      }

      window.requestAnimationFrame(step);
    }

    hydrateLiveStats(counters).then(function () {
      if (!("IntersectionObserver" in window)) {
        counters.forEach(animateCounter);
        return;
      }

      var observer = new IntersectionObserver(
        function (entries, instance) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              animateCounter(entry.target);
              instance.unobserve(entry.target);
            }
          });
        },
        {
          threshold: 0.35,
        }
      );

      counters.forEach(function (counter) {
        observer.observe(counter);
      });
    });
  });
})();
