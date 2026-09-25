// OpenClass shared behaviour. Progress is kept in memory only; nothing is stored.
(function () {
  var button = document.getElementById("mark-complete");
  var status = document.getElementById("lesson-status");
  if (!button || !status) {
    return;
  }
  button.addEventListener("click", function () {
    var done = button.getAttribute("aria-pressed") === "true";
    button.setAttribute("aria-pressed", done ? "false" : "true");
    status.textContent = done ? "Lesson marked as not complete." : "Lesson marked as complete.";
  });
})();
