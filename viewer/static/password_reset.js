document.getElementById('password-reset-form').addEventListener('submit', function(event) {
    var password = document.getElementById('id_new_password').value;
    var passwordConfirm = document.getElementById('id_new_password_confirm').value;
    var errorMessage = '';

    // Password validation
    if (password.length < 8) {
        errorMessage += '<strong>Zadané heslo je příliš krátké.</strong><br>';
    }
    if (!/[A-Z]/.test(password)) {
        errorMessage += '<strong>Zadané heslo neobsahuje velké písmeno.</strong><br>';
    }
    if (!/[a-z]/.test(password)) {
        errorMessage += '<strong>Zadané heslo neobsahuje malé písmeno.</strong><br>';
    }
    if (!/[0-9]/.test(password)) {
        errorMessage += '<strong>Heslo neobsahuje žádnou číslici.</strong><br>';
    }
    if (password !== passwordConfirm) {
        errorMessage += '<strong>Hesla se neshodují.</strong><br>';
    }

    if (errorMessage) {
        event.preventDefault();
        document.getElementById('error-messages').innerHTML = errorMessage;
    }
});