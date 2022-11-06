const search = document.getElementById('search');
const spinner = document.getElementById('spinner');

search.addEventListener('click', (e) => {
    spinner.classList.toggle('visible');
});