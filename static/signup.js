var validRegex = "/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/";
document.getElementById('email').addEventListener('change',mail_check);
    function mail_check(){
    org_email = document.getElementById('email').value;
    x = document.getElementById('email').value;
    x.value = x.value.toUpperCase();
    if (!org_email.match(validRegex)){
        document.getElementById('show_error').textContent = "Please enter a valid email address";
        document.getElementById('password').disable = true;
    }
}
