// Lesson media behaviour: rotating facts and the equation panel.
(function () {
  var slides = document.querySelectorAll("#facts-carousel .slide");
  var current = 0;
  setInterval(function () {
    slides[current].hidden = true;
    current = (current + 1) % slides.length;
    slides[current].hidden = false;
  }, 3000);

  var trigger = document.getElementById("more-trigger");
  var panel = document.getElementById("more-panel");
  trigger.addEventListener("click", function () {
    var open = trigger.getAttribute("aria-expanded") === "true";
    trigger.setAttribute("aria-expanded", open ? "false" : "true");
    panel.hidden = open;
  });
})();
