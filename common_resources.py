from cryptography.fernet import Fernet

# attributes
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

#html
signup_html = 'signup.html'
signin_html = 'signin.html'
home_html = 'home.html'
create_redirection_map_html = 'create_redirection_map.html'

# methods
def get_org_id(request):
    fer = Fernet(bytes(request.session["fk"],'utf-8'))
    decr_id = int(fer.decrypt(bytes(request.session["sk"],'utf-8')).decode())
    return decr_id