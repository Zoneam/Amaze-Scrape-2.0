const spinner = document.getElementById("spinner");

$(".loading").on("click", () => {
  spinner.classList.toggle("visible");
});

$(document).ready(function () {
  // Bounce button
  $(".loading").on("click", function () {
    const element = document.querySelector("#search");
    element.classList.add("animated", "swing");
    setTimeout(function () {
      element.classList.remove("swing");
    }, 1000);
  });
 
});
