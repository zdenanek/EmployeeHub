// Příklad jednoduchého JavaScriptu pro rozbalení a sbalení navigační lišty
document.addEventListener('DOMContentLoaded', function() {
    var navbarToggler = document.querySelector('.navbar-toggler');
    var navbarCollapse = document.querySelector('#navbarSupportedContent');

    navbarToggler.addEventListener('click', function() {
        if (navbarCollapse.classList.contains('show')) {
            navbarCollapse.classList.remove('show');
        } else {
            navbarCollapse.classList.add('show');
        }
    });
});
