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


$(function() {

  $(".progress").each(function() {

    let value = $(this).attr('data-value');
    let left = $(this).find('.progress-left .progress-bar');
    let right = $(this).find('.progress-right .progress-bar');
    if (value > 0) {
      if (value <= 50) {
        right.css('transform', 'rotate(' + percentageToDegrees(value) + 'deg)')
      } else {
        right.css('transform', 'rotate(180deg)')
        left.css('transform', 'rotate(' + percentageToDegrees(value - 50) + 'deg)')
      }
    }
  })

  function percentageToDegrees(percentage) {
    return percentage / 100 * 360
  }

});
