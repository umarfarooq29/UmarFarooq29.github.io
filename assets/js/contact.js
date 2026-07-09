(function () {
  "use strict";

  var app = window.UmarPortfolio || {};
  var ready = app.whenReady || function (callback) { callback(); };

  function getStatus(form) {
    var status = form.querySelector("[data-form-status]");

    if (status) {
      return status;
    }

    status = document.createElement("div");
    status.className = "form-status";
    status.setAttribute("data-form-status", "");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    form.appendChild(status);
    return status;
  }

  function setStatus(status, message, type) {
    status.textContent = message;
    status.className = "form-status is-" + type;
  }

  function isValidEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  function validateField(field) {
    var value = field.value.trim();
    var isValid = true;

    if (field.required && !value) {
      isValid = false;
    }

    if (isValid && field.type === "email") {
      isValid = isValidEmail(value);
    }

    field.classList.toggle("is-invalid", !isValid);
    field.classList.toggle("is-valid", isValid && value.length > 0);
    field.setAttribute("aria-invalid", isValid ? "false" : "true");

    return isValid;
  }

  function validateForm(fields) {
    return fields.reduce(function (isFormValid, field) {
      return validateField(field) && isFormValid;
    }, true);
  }

  function getFirstInvalidField(fields) {
    return fields.find(function (field) {
      return field.classList.contains("is-invalid");
    });
  }

  function getFieldValue(form, name) {
    var field = form.querySelector("[name='" + name + "']");
    return field ? field.value.trim() : "";
  }

  function buildMailtoUrl(form) {
    var recipient = form.getAttribute("data-contact-email") || "umarfarooqapp.dev@gmail.com";
    var name = getFieldValue(form, "name");
    var email = getFieldValue(form, "email");
    var subject = getFieldValue(form, "subject") || "Portfolio contact message";
    var message = getFieldValue(form, "message");
    var body = [
      message,
      "",
      "From: " + name,
      "Email: " + email,
    ].join("\n");

    return "mailto:" + encodeURIComponent(recipient) +
      "?subject=" + encodeURIComponent(subject) +
      "&body=" + encodeURIComponent(body);
  }

  ready(function () {
    var forms = Array.from(document.querySelectorAll("[data-contact-form]"));

    forms.forEach(function (form) {
      var status = getStatus(form);
      var fields = Array.from(form.querySelectorAll("input:not([type='hidden']), textarea"));
      var submitButton = form.querySelector('[type="submit"]');
      var defaultButtonText = submitButton ? submitButton.textContent : "";

      fields.forEach(function (field) {
        field.addEventListener("input", function () {
          if (field.classList.contains("is-invalid") || field.classList.contains("is-valid")) {
            validateField(field);
          }

          if (status.textContent) {
            setStatus(status, "", "idle");
          }
        });

        field.addEventListener("blur", function () {
          if (field.value.trim()) {
            validateField(field);
          }
        });
      });

      form.addEventListener("submit", function (event) {
        event.preventDefault();

        if (!validateForm(fields)) {
          var firstInvalid = getFirstInvalidField(fields);
          setStatus(status, "Please complete the highlighted fields before sending.", "error");

          if (firstInvalid) {
            firstInvalid.focus();
          }

          return;
        }

        if (submitButton) {
          submitButton.disabled = true;
          submitButton.textContent = "Opening email...";
        }

        setStatus(status, "Opening your email app with the message ready to send.", "success");
        window.setTimeout(function () {
          window.location.href = buildMailtoUrl(form);

          if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = defaultButtonText;
          }
        }, 150);
      });
    });
  });
})();
