const spinner = document.getElementById('spinner');

$("#search").click((e) => {
    spinner.classList.toggle('visible');
});

$( document ).ready(function() {
    // Bounce button
    $("#search").click(function(){
        console.log("clicked");
        const element =  document.querySelector('#search');
        element.classList.add('animated', 'swing');
        setTimeout(function() {
          element.classList.remove('swing'); 
  },        1000); 
    });
    
    
}); 
