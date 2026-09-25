// Quiz sign-up behaviour. Nothing is sent or stored; the form only shows a status message.
(function () {
  var form = document.getElementById("signup-form");
  var email = document.getElementById("email");
  var date = document.getElementById("quiz-date");
  var submit = document.getElementById("submit-signup");
  var status = document.getElementById("form-status");
  var agree = document.getElementById("agree");
  var course = document.getElementById("course-select");
  var termsFirst = document.getElementById("terms-first");
  var termsLast = document.getElementById("terms-last");
  var closeTerms = document.getElementById("close-terms");

  course.addEventListener("change", function () {
    if (course.value === "maths" || course.value === "writing") {
      window.location.href = "index.html";
    }
  });

  termsLast.addEventListener("keydown", function (event) {
    if (event.key === "Tab" && !event.shiftKey) {
      event.preventDefault();
      termsFirst.focus();
    }
  });
  termsFirst.addEventListener("keydown", function (event) {
    if (event.key === "Tab" && event.shiftKey) {
      event.preventDefault();
      termsLast.focus();
    }
  });

  closeTerms.addEventListener("click", function () {
    document.getElementById("terms-box").hidden = true;
  });

  agree.addEventListener("click", function () {
    agree.classList.toggle("is-checked");
  });

  Array.prototype.forEach.call(document.querySelectorAll(".help-icon"), function (button) {
    button.addEventListener("click", function () {
      var target = document.getElementById(button.getAttribute("data-help"));
      target.hidden = !target.hidden;
    });
  });

  submit.addEventListener("click", function () {
    var ok = true;
    email.classList.remove("invalid");
    date.classList.remove("invalid");
    if (!email.value || email.value.indexOf("@") < 1) {
      email.classList.add("invalid");
      ok = false;
    }
    if (!/^\d{2}\/\d{2}\/\d{4}$/.test(date.value)) {
      date.classList.add("invalid");
      ok = false;
    }
    if (ok) {
      status.textContent = "You are signed up. The quiz link is on your course page.";
      form.reset();
    }
  });
})();
