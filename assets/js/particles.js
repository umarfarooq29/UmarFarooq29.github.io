(function () {
  "use strict";

  var app = window.UmarPortfolio || {};
  var ready = app.whenReady || function (callback) { callback(); };
  var prefersReducedMotion = app.prefersReducedMotion || function () { return false; };

  ready(function () {
    var canvas = document.getElementById("particleCanvas");

    if (!canvas) {
      return;
    }

    var context = canvas.getContext("2d", {
      alpha: true,
    });

    if (!context) {
      return;
    }

    var particles = [];
    var animationFrameId = null;
    var isPaused = false;
    var reducedMotion = prefersReducedMotion();
    var pixelRatio = Math.min(window.devicePixelRatio || 1, 2);

    function getThemeColors() {
      var isDark = document.documentElement.getAttribute("data-theme") === "dark";

      return {
        point: isDark ? "rgba(125, 211, 252, 0.42)" : "rgba(37, 99, 235, 0.26)",
        line: isDark ? "rgba(20, 184, 166, 0.16)" : "rgba(14, 165, 233, 0.12)",
      };
    }

    function resizeCanvas() {
      var rect = canvas.getBoundingClientRect();
      pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.floor(rect.width * pixelRatio));
      canvas.height = Math.max(1, Math.floor(rect.height * pixelRatio));
      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      createParticles(rect.width, rect.height);
      draw();
    }

    function createParticles(width, height) {
      var count = Math.min(58, Math.max(18, Math.floor((width * height) / 24000)));

      particles = Array.from({ length: count }, function () {
        return {
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.22,
          vy: (Math.random() - 0.5) * 0.22,
          size: Math.random() * 1.7 + 0.8,
        };
      });
    }

    function update(width, height) {
      particles.forEach(function (particle) {
        particle.x += particle.vx;
        particle.y += particle.vy;

        if (particle.x < 0 || particle.x > width) {
          particle.vx *= -1;
        }

        if (particle.y < 0 || particle.y > height) {
          particle.vy *= -1;
        }
      });
    }

    function drawConnections(colors) {
      var maxDistance = 132;

      for (var i = 0; i < particles.length; i += 1) {
        for (var j = i + 1; j < particles.length; j += 1) {
          var first = particles[i];
          var second = particles[j];
          var dx = first.x - second.x;
          var dy = first.y - second.y;
          var distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < maxDistance) {
            context.globalAlpha = 1 - distance / maxDistance;
            context.strokeStyle = colors.line;
            context.lineWidth = 1;
            context.beginPath();
            context.moveTo(first.x, first.y);
            context.lineTo(second.x, second.y);
            context.stroke();
          }
        }
      }

      context.globalAlpha = 1;
    }

    function drawPoints(colors) {
      context.fillStyle = colors.point;

      particles.forEach(function (particle) {
        context.beginPath();
        context.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        context.fill();
      });
    }

    function draw() {
      var rect = canvas.getBoundingClientRect();
      var colors = getThemeColors();

      context.clearRect(0, 0, rect.width, rect.height);
      drawConnections(colors);
      drawPoints(colors);
    }

    function animate() {
      if (isPaused || reducedMotion) {
        return;
      }

      var rect = canvas.getBoundingClientRect();
      update(rect.width, rect.height);
      draw();
      animationFrameId = window.requestAnimationFrame(animate);
    }

    function start() {
      if (reducedMotion || animationFrameId) {
        return;
      }

      animationFrameId = window.requestAnimationFrame(animate);
    }

    function stop() {
      if (animationFrameId) {
        window.cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
      }
    }

    resizeCanvas();
    start();

    window.addEventListener("resize", app.throttle ? app.throttle(resizeCanvas, 180) : resizeCanvas, { passive: true });
    window.addEventListener("portfolio:themechange", draw);

    document.addEventListener("visibilitychange", function () {
      isPaused = document.hidden;

      if (isPaused) {
        stop();
      } else {
        start();
      }
    });
  });
})();
