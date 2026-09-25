// Quiz sign-up behaviour. Nothing is sent or stored; the form only shows a status message.
(function () {
  var form = document.getElementById("signup-form");
  var email = document.getElementById("email");
  var emailError = document.getElementById("email-error");
  var date = document.getElementById("quiz-date");
  var dateError = document.getElementById("quiz-date-error");
  var submit = document.getElementById("submit-signup");
  var status = document.getElementById("form-status");
  var agree = document.getElementById("agree");
  var closeTerms = document.getElementById("close-terms");

  closeTerms.addEventListener("click", function () {
    document.getElementById("terms-box").hidden = true;
  });

  agree.addEventListener("click", function () {
    var checked = agree.getAttribute("aria-checked") === "true";
    agree.setAttribute("aria-checked", checked ? "false" : "true");
    agree.classList.toggle("is-checked");
  });

  Array.prototype.forEach.call(document.querySelectorAll(".help-icon"), function (button) {
    button.addEventListener("click", function () {
      var target = document.getElementById(button.getAttribute("data-help"));
      target.hidden = !target.hidden;
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      Array.prototype.forEach.call(document.querySelectorAll(".help-icon"), function (button) {
        var target = document.getElementById(button.getAttribute("data-help"));
        if (target) { target.hidden = true; }
      });
    }
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var ok = true;
    email.classList.remove("invalid");
    email.removeAttribute("aria-invalid");
    emailError.hidden = true;
    emailError.textContent = "";
    date.classList.remove("invalid");
    date.removeAttribute("aria-invalid");
    dateError.hidden = true;
    dateError.textContent = "";

    if (!email.value || email.value.indexOf("@") < 1) {
      email.classList.add("invalid");
      email.setAttribute("aria-invalid", "true");
      emailError.textContent = "Enter a valid email address, for example name@example.com";
      emailError.hidden = false;
      ok = false;
    }
    if (!/^\d{2}\/\d{2}\/\d{4}$/.test(date.value)) {
      date.classList.add("invalid");
      date.setAttribute("aria-invalid", "true");
      dateError.textContent = "Enter the date as DD/MM/YYYY, for example 25/09/2026";
      dateError.hidden = false;
      ok = false;
    }
    if (ok) {
      status.textContent = "You are signed up. The quiz link is on your course page.";
      form.reset();
    }
  });
})();
